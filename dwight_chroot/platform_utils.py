import os
import pwd
import subprocess
from .exceptions import CommandFailed
    
def get_user_shell():
    return pwd.getpwuid(os.getuid()).pw_shell

def execute_command_assert_success(cmd, **kw):
    returned = execute_command(cmd, **kw)
    if returned.returncode != 0:
        raise CommandFailed("Command {0!r} failed with exit code {1}".format(cmd, returned.returncode))
    return returned

def execute_command(cmd, **kw):
    returned = subprocess.Popen(cmd, shell=True, **kw)
    returned.wait()
    return returned

