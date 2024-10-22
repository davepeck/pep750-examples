"""Examples of lazy evaluation in templates."""

from . import Template
from .fstring import convert


def format_some(selector: str, template: Template, ignored: str = "***") -> str:
    """
    Given a template where all interpolations are callables, invoke the
    callables only when the format_spec is `:selector`.
    """
    parts = []
    for t_arg in template.args:
        if isinstance(t_arg, str):
            parts.append(t_arg)
        else:
            if not callable(t_arg.value):
                raise ValueError(f"Non-callable interpolation: {t_arg.value}")
            if t_arg.format_spec == selector:
                value = t_arg.value()
                value = convert(value, t_arg.conv)
            else:
                value = ignored
            parts.append(value)
    return "".join(parts)
