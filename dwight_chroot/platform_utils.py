import os
import pwd
    
def get_user_shell():
    return pwd.getpwuid(os.getuid()).pw_shell
