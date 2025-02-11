"""Experimental module to automatically install Friendly
as a replacement for the standard traceback in IDLE."""

import inspect
from pathlib import Path
import sys  # noqa


from idlelib import run as idlelib_run

import friendly_traceback  # noqa
from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import helpers, FriendlyHelpers  # noqa

from ..my_gettext import current_lang
from . import idle_formatter
from . import patch_source_cache  # noqa


friendly_traceback.exclude_file_from_traceback(__file__)

Friendly = FriendlyHelpers()
Friendly.__friendly_repr__ = Friendly.__repr__
helpers["Friendly"] = Friendly

_set_formatter = set_formatter  # noqa
_set_lang = set_lang  # noqa


def set_lang(lang):
    current_lang.install(lang)
    _set_lang(lang)


set_lang.__rich_repr__ = _set_lang.__rich_repr__  # noqa


def set_formatter(formatter=None):
    if formatter == "idle":
        _set_formatter(idle_formatter.idle_formatter)
    else:
        _set_formatter(formatter=formatter)


set_formatter.__rich_repr__ = _set_formatter.__rich_repr__  # noqa

__all__ = list(helpers)
_old_displayhook = sys.displayhook


def _displayhook(value):
    if value is None:
        return
    if str(type(value)) == "<class 'function'>" and hasattr(value, "__rich_repr__"):
        idle_writer(
            [
                (f"    {value.__name__}():", "default"),
                (f" {value.__rich_repr__()[0]}", "stdout"),
                "\n",
            ]
        )
        return
    if hasattr(value, "__friendly_repr__"):
        lines = value.__friendly_repr__().split("\n")
        for line in lines:
            if "`" in line:
                newline = []
                parts = line.split("`")
                for index, content in enumerate(parts):
                    if index % 2 == 0:
                        newline.append((content, "stdout"))
                    else:
                        newline.append((content, "default"))
                newline.append("\n")
                idle_writer(newline)
            elif "():" in line:
                parts = line.split("():")
                idle_writer(
                    ((f"{    parts[0]}():", "default"), (parts[1], "stdout"), "\n")
                )
            else:
                idle_writer(line + "\n")
        return

    _old_displayhook(value)


def idle_writer(output, color=None):
    """Use this instead of standard sys.stderr to write traceback so that
    they can be colorized.
    """
    if isinstance(output, str):
        if color is None:
            sys.stdout.shell.write(output, "stderr")  # noqa
        else:
            sys.stdout.shell.write(output, color)  # noqa
        return
    for fragment in output:
        if isinstance(fragment, str):
            sys.stdout.shell.write(fragment, "stderr")  # noqa
        elif len(fragment) == 2:
            sys.stdout.shell.write(fragment[0], fragment[1])  # noqa
        else:
            sys.stdout.shell.write(fragment[0], "stderr")  # noqa


def install_in_idle_shell(lang="en"):
    """Installs Friendly in IDLE's shell so that it can retrieve
    code entered in IDLE's repl.
    Note that this requires Python version 3.10+ since IDLE did not support
    custom excepthook in previous versions of Python.

    Furthermore, Friendly is bypassed when code entered in IDLE's repl
    raises SyntaxErrors.
    """
    friendly_traceback.exclude_file_from_traceback(idlelib_run.__file__)
    friendly_traceback.install(include="friendly_tb", redirect=idle_writer, lang=lang)

    # Current limitation
    idle_writer("                                WARNING\n", "ERROR")  # noqa
    idle_writer("Friendly cannot handle SyntaxErrors for code entered in the shell.\n")


def install(lang="en"):
    """Installs Friendly in the IDLE shell, with a custom formatter.
    For Python versions before 3.10, this was not directly supported, so a
    Friendly console is used instead of IDLE's shell.

    Changes introduced in Python 3.10 were back-ported to Python 3.9.5.
    """
    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_formatter(idle_formatter.idle_formatter)
    if sys.version_info >= (3, 9, 5):
        install_in_idle_shell(lang=lang)
        sys.displayhook = _displayhook
    else:
        idle_writer("Friendly cannot be installed in this version of IDLE.\n")
        idle_writer("Using Friendly's own console instead.\n")
        start_console(lang=lang, displayhook=_displayhook)


def start_console(lang="en", displayhook=None, ipython_prompt=True):
    """Starts a Friendly console with a custom formatter for IDLE"""
    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_stream(idle_writer)
    friendly_traceback.start_console(
        formatter=idle_formatter.idle_formatter,
        lang=lang,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )


def run(
    filename,
    lang=None,
    include="friendly_tb",
    args=None,
    console=True,
    ipython_prompt=True,
):
    """This function executes the code found in a Python file.

    ``filename`` should be either an absolute path or, it should be the name of a
    file (filename.py) found in the same directory as the file from which ``run()``
    is called.

    If friendly_console is set to ``False`` (the default) and the Python version
    is greater or equal to 3.10, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True`` (the default), the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currently only ``en`` (default) and ``fr``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised.

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...


    """
    _ = current_lang.translate

    sys.stderr = sys.stdout.shell  # noqa
    friendly_traceback.set_formatter(idle_formatter.idle_formatter)
    friendly_traceback.set_stream(idle_writer)

    filename = Path(filename)
    if not filename.is_absolute():
        frame = inspect.stack()[1]
        # This is the file from which run() is called
        run_filename = Path(frame[0].f_code.co_filename)
        run_dir = run_filename.parent.absolute()
        filename = run_dir.joinpath(filename)

    if not filename.exists():
        print(_("The file {filename} does not exist.").format(filename=filename))
        return

    if not console:
        if sys.version_info >= (3, 10):
            install_in_idle_shell()
        else:
            sys.stderr.write("Friendly cannot be installed in this version of IDLE.\n")

    return friendly_traceback.run(
        filename,
        lang=lang,
        include=include,
        args=args,
        console=console,
        formatter=idle_formatter.idle_formatter,
        ipython_prompt=ipython_prompt,
    )


__all__.append("install")
__all__.append("start_console")
__all__.append("run")
