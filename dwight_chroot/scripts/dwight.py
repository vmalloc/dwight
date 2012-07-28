#! /usr/bin/python
from __future__ import print_function
import argparse
import logging
import sys
from ..environment import Environment
from ..exceptions import UsageException

#################################### Actions ###################################

def _run_shell(env, args):
    return env.run_shell()

def _run_cmd(env, args):
    return env.run_command_in_chroot(args.cmd)
    
################################## Boilerplate #################################

parser = argparse.ArgumentParser(usage="%(prog)s [options] action [action options/args]")
parser.add_argument("-c", "--config-file", dest="config_files", type=open, action="append", default=[])
parser.add_argument("-e", "--exclude-dwightrc", dest="exclude_user_config", action="store_true", default=False,
                    help="Don't use the default configuration file in ~/.dwightrc")
parser.add_argument("-v", action="append_const", const=1, dest="verbosity", default=[], 
                    help="Be more verbose. Can be specified multiple times to increase verbosity further")
subparsers = parser.add_subparsers(help="Action to be taken")

shell_command_parser = subparsers.add_parser("shell", help="Run a shell inside the chrooted environment")
shell_command_parser.set_defaults(action=_run_shell)

cmd_command_parser = subparsers.add_parser("cmd", help="Run a command inside the chrooted environment")
cmd_command_parser.set_defaults(action=_run_cmd)
cmd_command_parser.add_argument("cmd")

def main(args):
    env = Environment()

    if not args.exclude_user_config:
        env.config.process_user_config_file()

    for config_file in args.config_files:
        env.config.load_from_string(config_file.read())
    try:
        return args.action(env, args)
    except UsageException as e:
        print(str(e), file=sys.stderr)
        return -1

def _configure_logging(args):
    verbosity_level = len(args.verbosity)
    if verbosity_level == 0:
        level = "WARNING"
    elif verbosity_level == 1:
        level = "INFO"
    else:
        level = "DEBUG"
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(asctime)s -- %(message)s"
        )

#### For use with entry_points/console_scripts
def main_entry_point():
    args = parser.parse_args()
    _configure_logging(args)
    sys.exit(main(args))
if __name__ == "__main__":
    main_entry_point()
