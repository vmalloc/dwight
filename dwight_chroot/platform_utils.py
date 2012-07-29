import ctypes
from contextlib import contextmanager
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

def execute_command_assert_success(cmd, **kw):
    returned = execute_command(cmd, **kw)
    if returned.returncode != 0:
        raise CommandFailed("Command {0!r} failed with exit code {1}".format(cmd, returned.returncode))
    return returned

def execute_command(cmd, unsudo=False, **kw):
    if unsudo:
        cmd = _get_unsudo_command(cmd)
    _logger.debug("Running %r (%s)", cmd, kw)
    returned = subprocess.Popen(cmd, shell=True, **kw)
    returned.wait()
    _logger.debug("%r finished with exit code %s", cmd, returned.returncode)
    return returned

def _get_unsudo_command(cmd):
    sudo_uid = get_sudo_uid()
    sudo_gid = get_sudo_gid()
    if not sudo_uid and not sudo_gid:
        return cmd
    prefix = "sudo "
    if sudo_uid is not None:
        prefix += "-u \\#{0} ".format(sudo_uid)
    if sudo_gid is not None:
        prefix += "-g \\#{0} ".format(sudo_gid)
    return prefix + cmd 

def get_sudo_uid():
    return _int_if_not_none(os.environ.get("SUDO_UID"))
def get_sudo_gid():
    return _int_if_not_none(os.environ.get("SUDO_GID"))
def get_sudo_groups():
    sudo_uid = get_sudo_uid()
    if sudo_uid is None:
        return None
    return get_groups_by_uid(sudo_uid)

def get_groups_by_uid(uid):
    try:
        username = pwd.getpwuid(uid).pw_name
    except KeyError:
        _logger.warning("Failed to get pwd information for uid %s", uid, exc_info=True)
        return []
    gids = [g.gr_gid for g in grp.getgrall() if username in g.gr_mem]
    return gids

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

@contextmanager
def unsudo_context():
    old_uid = os.geteuid()
    old_gid = os.getegid()
    sudo_uid = get_sudo_uid()
    sudo_gid = get_sudo_gid()
    if sudo_gid is not None:
        _logger.debug("Changing gid to %s", sudo_gid)
        os.setegid(sudo_gid)
    if sudo_uid is not None:
        _logger.debug("Changing uid to %s", sudo_uid)
        os.seteuid(sudo_uid)
    try:
        yield
    finally:
        os.seteuid(old_uid)
        os.setegid(old_gid)

def _int_if_not_none(value):
    if value is not None:
        value = int(value)
    return value
