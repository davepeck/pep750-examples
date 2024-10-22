"""Examples of lazy evaluation in templates."""

from . import Template
from .fstring import convert


def format_some(selector: str, template: Template, ignored: str = "***") -> str:
    """
    Render a template to string in a stylized way.

    Render only those interpolations whose `format_spec` matches `selector`.

    In addition, if an interpolation is a callable, only invoke it when the
    `format_spec` matches `selector`. This allows us to defer computation
    until we know it's needed; for instance, in a logging pipeline where
    some expressions are expensive to compute and later prove to be
    unnecessary.
    """
    parts = []
    for t_arg in template.args:
        if isinstance(t_arg, str):
            parts.append(t_arg)
        else:
            if t_arg.format_spec == selector:
                value = t_arg.value
                if callable(value):
                    value = value()
                value = convert(value, t_arg.conv)
            else:
                value = ignored
            parts.append(value)
    return "".join(parts)
