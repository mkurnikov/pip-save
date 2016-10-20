import locale
import os
import sys

from pip import PipError
from pip import commands_dict, check_isolated, autocomplete, parseopts
from pip import logger
from pip.utils import deprecation

from pip_save.commands.install import MyInstallCommand


TOML_FILE_NAME = 'pypm.toml'

commands_dict[MyInstallCommand.name] = MyInstallCommand


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Configure our deprecation warnings to be sent through loggers
    deprecation.install_warning_logger()

    autocomplete()

    try:
        cmd_name, cmd_args = parseopts(args)
    except PipError as exc:
        sys.stderr.write("ERROR: %s" % exc)
        sys.stderr.write(os.linesep)
        sys.exit(1)

    # Needed for locale.getpreferredencoding(False) to work
    # in pip.utils.encoding.auto_decode
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error as e:
        # setlocale can apparently crash if locale are uninitialized
        logger.debug("Ignoring error %s when setting locale", e)

    command = commands_dict[cmd_name](isolated=check_isolated(cmd_args))
    return command.main(cmd_args)
