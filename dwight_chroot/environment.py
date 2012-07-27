import logging
import os
import platform
import string
import subprocess
import sys

if platform.system().lower() == "linux":
    import unshare
else:
    # for testing purposes on systems which are not Linux...
    unshare = None

from .cache import Cache
from .config import DwightConfiguration
from .exceptions import NotRootException
from .platform_utils import (
    execute_command,
    execute_command_assert_success,
    get_user_shell,
    )
from .python_compat import iteritems
from .resources import Resource

_logger = logging.getLogger(__name__)

_DWIGHT_CACHE_DIR = os.path.expanduser("~/.dwight-cache")
_ROOT_IMAGE_MOUNT_PATH = os.path.join(_DWIGHT_CACHE_DIR, "mounts", "root_image")

class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
        self.cache = Cache(os.path.expanduser("~/.dwight-cache"))
        self.config = DwightConfiguration()
    ############################################################################
    def run_shell(self):
        self.run_command_in_chroot(get_user_shell())
    def run_command_in_chroot(self, cmd):
        if os.getuid() != 0:
            raise NotRootException("Dwight must be run as root")
        self.config.check()
        child_pid = os.fork()
        if child_pid == 0:
            self._run_command_in_chroot_as_forked_child(cmd)
        else:
            return self._wait_for_forked_child(child_pid)
    def _run_command_in_chroot_as_forked_child(self, cmd):
        try:
            self._unshare_mount_points()
            path = self._mount_base_image()
            self._mount_includes(path)
            os.chroot(path)
            self._setuid()
            p = execute_command(
                "env {env} {cmd}".format(
                    env=" ".join('{0}="{1}"'.format(key, value) for key, value in iteritems(self.config["ENVIRON"])),
                    cmd=cmd)
                    )
            os._exit(p.wait())
        except Exception:
            _logger.error("Error occurred running command", exc_info=True)
            raise
    def _wait_for_forked_child(self, child_pid):
        _, exit_code = os.waitpid(child_pid, 0)
        exit_code >>= 8
        _logger.debug("_wait_for_forked_child: child returned %s", exit_code)
        return exit_code
    def _setuid(self):
        uid = self.config["UID"]
        if uid is None:
            uid = self._try_get_sudo_uid()
        if uid is not None:
            os.setuid(uid)
    def _try_get_sudo_uid(self):
        sudo_uid = os.environ.get("SUDO_UID")
        if sudo_uid is not None:
            return int(sudo_uid)
            
    def _unshare_mount_points(self):
        if unshare is None:
            raise PlatformNotSupported("{0} is not supported".format(platform.system()))
        _logger.debug("calling unshare()")
        unshare.unshare(unshare.CLONE_NEWNS)
    def _mount_base_image(self):
        if not os.path.isdir(_ROOT_IMAGE_MOUNT_PATH):
            os.makedirs(_ROOT_IMAGE_MOUNT_PATH)
        root_image = Resource.from_string(self.config["ROOT_IMAGE"])
        _logger.debug("Mounting base image %r in %r", root_image, _ROOT_IMAGE_MOUNT_PATH)
        root_image_path = root_image.get_path(self)
        self._mount_regular_file(root_image_path, _ROOT_IMAGE_MOUNT_PATH)
        return _ROOT_IMAGE_MOUNT_PATH
    def _mount_includes(self, base_path):
        for include in self.config["INCLUDES"]:
            _logger.debug("Fetching include %s...", include)
            path = include.to_resource().get_path(self)
            self._mount_path(path, base_path, include.dest)
    def _mount_path(self, path, base_path, mount_point):
        path = os.path.abspath(path)
        if os.path.isabs(mount_point):
            mount_point = os.path.relpath(mount_point, '/')
        mount_point = os.path.join(base_path, mount_point)
        if not os.path.exists(path):
            raise CannotMountPath("Cannot mount {0}: does not exist".format(path))
        if os.path.isfile(path):
            return self._mount_regular_file(path, mount_point)
        return self._mount_directory(path, mount_point)
    def _mount_regular_file(self, path, mount_point):
        _logger.debug("Mounting squashfs file %r to %s", path, mount_point)
        execute_command_assert_success("mount -n -t squashfs -o loop {0} {1}".format(path, mount_point))
    def _mount_directory(self, path, mount_point):
        _logger.debug("Mounting (binding) %r to %s", path, mount_point)
        execute_command_assert_success("mount -n --bind {0} {1}".format(path, mount_point))
