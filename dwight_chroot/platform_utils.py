import ctypes
import errno
import logging
import os
import platform
import pwd
import grp
import subprocess
from .exceptions import CommandFailed

_logger = logging.getLogger(__name__)

def get_current_user_shell():
    return pwd.getpwuid(os.getuid()).pw_shell

def get_user_groups(uid):
    try:
        username = pwd.getpwuid(uid).pw_name
    except KeyError:
        return []

    gids = [g.gr_gid for g in grp.getgrall() if username in g.gr_mem]
    return gids

def execute_command_assert_success(cmd, **kw):
    returned = execute_command(cmd, **kw)
    if returned.returncode != 0:
        raise CommandFailed("Command {0!r} failed with exit code {1}".format(cmd, returned.returncode))
    return returned

def execute_command(cmd, **kw):
    _logger.debug("Running %r (%s)", cmd, kw)
    returned = subprocess.Popen(cmd, shell=True, **kw)
    returned.wait()
    _logger.debug("%r finished with exit code %s", cmd, returned.returncode)
    return returned


if platform.system() == "Linux":
    CLONE_NEWNS = 131072
    _libc = ctypes.CDLL("libc.so.6")
    def unshare_mounts():
        return_value = _libc.unshare(CLONE_NEWNS)
        if 0 != return_value:
            errno_val = ctypes.get_errno()
            raise OSError("unshare() called failed (errno={0} ({1}))".format(
                errno_val, errno.errorcode.get(errno_val, "?")
                ))
else:
    def unshare_mounts():
        raise NotImplementedError("Only supported on Linux") 
        
