"""
Implement f-string like behavior on top of t-strings.

Template strings are a generalization of f-strings. t-strings evaluate
to a new type (`Template`); it is possible to take a `Template` and build
a string that exactly matches the result had an `f`-prefix been used in the
first place.

See also `test_fstring.py`
"""

from typing import Literal

from templatelib import Interpolation, Template

from . import pairs


def convert(value: object, conv: Literal["a", "r", "s"] | None) -> object:
    """Convert the value to a string using the specified conversion."""
    # Python has no convert() built-in function, so we have to implement it.
    # For our purposes, we allow `conv` to be `None`; in practice, I imagine
    # if Python had a real convert() method, that wouldn't be part of the
    # type signature, and we'd return str.
    if conv == "a":
        return ascii(value)
    if conv == "r":
        return repr(value)
    if conv == "s":
        return str(value)
    return value


def f(template: Template) -> str:
    """Implement f-string behavior using the PEP 750 t-string behavior."""
    parts = []
    for i, s in pairs(template):
        if i is not None:
            value = convert(i.value, i.conv)
            value = format(value, i.format_spec)
            parts.append(value)
        parts.append(s)
    return "".join(parts)
