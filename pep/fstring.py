"""
Implement f-string like behavior on top of t-strings.

Tempalate strings are a generalization of f-strings. t-strings evaluate
to a new type (`Template`); it is possible to take a `Template` and build
a string that exactly matches the result had an `f`-prefix been used in the
first place.

See also test_fstring.py
"""

from typing import Any, Literal

from . import Interpolation, Template


def convert(value: Any, conv: Literal["a", "r", "s"] | None) -> Any:
    if conv == "a":
        return ascii(value)
    elif conv == "r":
        return repr(value)
    elif conv == "s":
        return str(value)
    return value


def f(template: Template) -> str:
    """Implement f-string behavior using the PEP 750 t-string behavior."""
    parts = []
    for arg in template.args:
        match arg:
            case str() as s:
                parts.append(s)
            case Interpolation(value, _, format_spec, conv):
                value = convert(value, conv)
                value = format(value, format_spec)
                parts.append(value)
    return "".join(parts)
