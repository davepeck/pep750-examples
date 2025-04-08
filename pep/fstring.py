"""
Implement f-string like behavior on top of t-strings.

Template strings are a generalization of f-strings. t-strings evaluate
to a new type (`Template`); it is possible to take a `Template` and build
a string that exactly matches the result had an `f`-prefix been used in the
first place.

See also `test_fstring.py`
"""

from string.templatelib import Interpolation, Template
from typing import Literal


def convert(value: object, conversion: Literal["a", "r", "s"] | None) -> object:
    """Convert the value to a string using the specified conversion."""
    # Python has no convert() built-in function, so we have to implement it.
    if conversion == "a":
        return ascii(value)
    if conversion == "r":
        return repr(value)
    if conversion == "s":
        return str(value)
    return value


def f(template: Template) -> str:
    """Implement f-string behavior using the PEP 750 t-string behavior."""
    parts = []
    for item in template:
        match item:
            case str() as s:
                parts.append(s)
            case Interpolation(value, _, conversion, format_spec):
                value = convert(value, conversion)
                value = format(value, format_spec)
                parts.append(value)
    return "".join(parts)
