"""Examples of lazy evaluation in templates."""

from templatelib import Template

from . import pairs
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
    for i, s in pairs(template):
        if i is not None:
            if i.format_spec == selector:
                value = i.value
                if callable(value):
                    value = value()
                value = convert(value, i.conv)
            else:
                value = ignored
            parts.append(value)
        parts.append(s)
    return "".join(parts)
