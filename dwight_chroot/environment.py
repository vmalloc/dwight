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
from .cache import Cache
from .include import Include
from .exceptions import (
    CannotLoadConfiguration,
    CommandFailed,
    InvalidConfiguration,
    NotRootException,
    UnknownConfigurationOptions,
    )
from .platform_utils import get_user_shell
from .resources import Resource

_logger = logging.getLogger(__name__)

class Environment(object):
    def __init__(self):
        super(Environment, self).__init__()
        self.reset_configuration()
        self.cache = Cache(os.path.expanduser("~/.dwight-cache"))
    def reset_configuration(self):
        self.base_image = None
        self.includes = []
        self.environ = {}
    def load_configuration_file(self, filename):
        with open(filename, "r") as configuration_file:
            self.load_configuration_string(configuration_file.read())
    def load_configuration_string(self, s):
        d = {}
        try:
            exec(s, {"Include" : Include}, d)
        except Exception as e:
            raise CannotLoadConfiguration("Cannot load configuration ({0})".format(e))
        self.reset_configuration()
        if "ROOT_IMAGE" not in d:
            raise InvalidConfiguration("ROOT_IMAGE is missing in configuration")
        self.base_image = Resource.from_string(d.pop("ROOT_IMAGE"))
        self.includes = d.pop("INCLUDES", [])
        self.environ = d.pop("ENVIRON", {})
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
        self._mount_includes(path)
        p = self._execute_command("env {env} /usr/sbin/chroot {path} {cmd}".format(
            env=" ".join('{0}="{1}"'.format(key, value) for key, value in self.environ.iteritems()),
            path=path,
            cmd=cmd))
        return p
    def _unshare_mount_points(self):
        if unshare is None:
            raise PlatformNotSupported("{0} is not supported".format(platform.system()))
        _logger.debug("calling unshare()")
        unshare.unshare(unshare.CLONE_NEWNS)
    def _mount_base_image(self):
        path = mkdtemp()
        _logger.debug("Mounting base image %r in %r", self.base_image, path)
        base_image_path = self.base_image.get_path(self)
        self._execute_command_assert_success("mount -n -t squashfs -o loop {0} {1}".format(base_image_path, path))
        return path
    def _mount_includes(self, base_path):
        for mount_point, include in self.includes.iteritems():
            _logger.debug("Fetching include %s...", include)
            path = include.to_resource().get_path(self)
            self._mount_path(path, base_path, mount_point)
    def _mount_path(self, path, base_path, mount_point):
        path = os.path.abspath(path)
        if os.path.isabs(mount_point):
            mount_point = os.path.relpath(mount_point, '/')
        mount_point = os.path.join(base_path, mount_point)
        _logger.debug("Mounting (binding) %r to %s", path, mount_point)
        self._execute_command_assert_success("mount -n --bind {0} {1}".format(path, mount_point))
    def _execute_command_assert_success(self, cmd, **kw):
        returned = self._execute_command(cmd, **kw)
        if returned.returncode != 0:
            raise CommandFailed("Command {0!r} failed with exit code {1}".format(cmd, returned))
        return returned
    def _execute_command(self, cmd, **kw):
        returned = subprocess.Popen(cmd, shell=True, **kw)
        returned.wait()
        return returned


                
