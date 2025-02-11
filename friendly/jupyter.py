from rich import jupyter as rich_jupyter

from friendly_traceback import session  # noqa
from .ipython import *  # noqa
from .ipython import helpers
from friendly import rich_formatters
from friendly.my_gettext import current_lang


# For Jupyter output, Rich specifies a set of fonts starting with Menlo and
# ending with monospace as last resort whereas Jupyter notebooks just
# specify monospace. To make font-size more consistent, we remove the
# font-specification from Rich.
rich_jupyter.JUPYTER_HTML_FORMAT = (
    "<pre style='white-space:pre;overflow-x:auto;line-height:normal'>{code}</pre>"
)


old_set_formatter = set_formatter  # noqa


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    session.rich_add_vspace = False
    session.use_rich = True
    if formatter == "jupyter":
        set_formatter(rich_formatters.jupyter)
    else:
        old_set_formatter(
            formatter=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )


set_formatter.help = old_set_formatter.help
set_formatter.__rich_repr__ = old_set_formatter.__rich_repr__
helpers["set_formatter"] = set_formatter
Friendly.set_formatter = set_formatter  # noqa

old_light = light  # noqa
old_dark = dark  # noqa


def light():
    set_formatter("interactive")


def dark():
    set_formatter("interactive-dark")


light.help = old_light.help  # noqa
light.__rich_repr__ = old_light.__rich_repr__  # noqa
light.__doc__ = old_light.__doc__
Friendly.light = light  # noqa
helpers["light"] = light

dark.help = old_dark.help  # noqa
dark.__rich_repr__ = old_dark.__rich_repr__  # noqa
dark.__doc__ = old_dark.__doc__
Friendly.dark = dark  # noqa
helpers["dark"] = dark


def set_tb_width(width=None):
    """Sets the width of the traceback when using a rich-based
    formatter in a Jupyter notebook or equivalent.

    The width of traceback is never less than the width of
    the other output from rich.
    """
    _ = current_lang.translate
    if width is None:
        return
    try:
        session.console.width = width
    except Exception:
        print(_("set_width() has no effect with this formatter."))
        return
    session.rich_tb_width = width
    if session.rich_width is None or session.rich_width > session.rich_tb_width:
        session.rich_width = width


setattr(Friendly, "set_tb_width", set_tb_width)  # noqa
helpers["set_tb_width"] = set_tb_width

__all__ = list(helpers.keys())

# Use the new interactive light formatter by default.

light()  # noqa
set_tb_width(100)  # noqa
set_width(70)  # noqa
session.is_jupyter = True
