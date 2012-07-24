import logging
import os
import platform
import string
import subprocess
from tempfile import mkdtemp

if platform.system().lower() == "linux":
    import unshare
else:
    # for testing purposes on systems which are not Linux...
    unshare = None
from .exceptions import (
    CannotLoadConfiguration,
    InvalidConfiguration,
    NotRootException,
    UnknownConfigurationOptions,
    )
from .platform_utils import get_user_shell

_logger = logging.getLogger(__name__)

class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
        self.reset_configuration()
    def reset_configuration(self):
        self.base_image = None
        self.extras = []
        self.environ = {}
        self.bind_mounts = {}
    def load_configuration_file(self, filename):
        with open(filename, "r") as configuration_file:
            self.load_configuration_string(configuration_file.read())
    def load_configuration_string(self, s):
        d = {}
        try:
            exec(s, {}, d)
        except Exception as e:
            raise CannotLoadConfiguration("Cannot load configuration ({0})".format(e))
        self.reset_configuration()
        if "ROOT_IMAGE" not in d:
            raise InvalidConfiguration("ROOT_IMAGE is missing in configuration")
        self.base_image = d.pop("ROOT_IMAGE")
        
        self.extras = d.pop("EXTRAS", [])
        self.environ = d.pop("ENVIRON", {})
        self.bind_mounts = d.pop("BIND_MOUNTS", {})
        unknown_parameters = self._get_unknown_parameters(d)
        if unknown_parameters:
            raise UnknownConfigurationOptions("Unknown options: {0}".format(", ".join(d)))
    def _get_unknown_parameters(self, configuration_dict):
        return [key for key in configuration_dict if key.isupper()]
    ############################################################################
    def run_shell(self):
        self.run_command_in_chroot(get_user_shell())
    def run_command_in_chroot(self, cmd):
        if os.getuid() != 0:
            raise NotRootException("Dwight must be run as root")
        self._unshare_mount_points()
        path = self._mount_base_image()
        self._mount_bind_mounts(path)
        self._execute_command("env {env} /usr/sbin/chroot {path} {cmd}".format(
            env=" ".join('{0}="{1}"'.format(key, value) for key, value in self.environ.iteritems()),
            path=path,
            cmd=cmd))
    def _unshare_mount_points(self):
        if unshare is None:
            raise PlatformNotSupported("{0} is not supported".format(platform.system()))
        _logger.debug("calling unshare()")
        unshare.unshare(unshare.CLONE_NEWNS)
    def _mount_base_image(self):
        path = mkdtemp()
        _logger.debug("Mounting base image %r in %r", self.base_image, path)
        self._execute_command_assert_success("mount -n -t squashfs -o loop {0} {1}".format(self.base_image, path))
        return path
    def _mount_bind_mounts(self, base_path):
        for mount_point, real_path in self.bind_mounts.iteritems():
            real_path = os.path.abspath(real_path)
            if os.path.isabs(mount_point):
                mount_point = os.path.relpath(mount_point, '/')
            mount_point = os.path.join(base_path, mount_point)
            _logger.debug("Mounting (binding) %r to %r", real_path, mount_point)
            self._execute_command_assert_success("mount -n --bind {0} {1}".format(real_path, mount_point))
    def _execute_command_assert_success(self, cmd, **kw):
        returned = self._execute_command(cmd, **kw)
        if returned != 0:
            raise CommandFailed("Command {0!r} failed with exit code {1}".format(cmd, returned))
    def _execute_command(self, cmd, **kw):
        return subprocess.call(cmd, shell=True, **kw)


                
