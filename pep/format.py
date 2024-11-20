"""
Example code to take an old-school format string intended to be used with the
`str.format()` method, and convert it to a modern `Template` instance.
"""

import re
import string
from typing import Literal

from templatelib import Interpolation, Template

type ParsedIndex = int | None
type ParsedKey = str | None
type ParsedConversion = Literal["a", "r", "s"] | None
type ParsedFormatSpec = str
type ParsedInterpolation = tuple[
    ParsedIndex, ParsedKey, ParsedFormatSpec, ParsedConversion
]


def _parse_fmt_string(fmt: str) -> tuple[str | ParsedInterpolation, ...]:
    """
    Parse a format string intended for use with `str.format()` and return a
    list of static string parts and interpolation parts. These parts are
    similar to, but not identical to, the parts of a `Template` instance;
    the from_format() function below takes care of the final conversion.

    This builds on top of string.Formatter.parse(), but has a slightly different
    return structure.
    """
    formatter = string.Formatter()
    parts: list[str | ParsedInterpolation] = []
    mode: Literal["auto", "manual"] | None = None
    auto_index = 0
    for literal_text, field_name, format_spec, conversion in formatter.parse(fmt):
        if literal_text:
            parts.append(literal_text)
        if field_name is not None:
            if field_name.isdigit():
                if mode is None:
                    mode = "manual"
                if mode != "manual":
                    raise ValueError(
                        "Cannot mix automatic field numbering with manual field numbering"
                    )
                index = int(field_name)
                key = None
            elif not field_name:
                if mode is None:
                    mode = "auto"
                if mode != "auto":
                    raise ValueError(
                        "Cannot mix automatic field numbering with manual field numbering"
                    )
                index = auto_index
                key = None
                auto_index += 1
            else:
                index = None
                key = field_name

            if conversion not in {"s", "r", "a", None}:
                raise ValueError(f"Invalid conversion specifier: {conversion}")
            format_spec = format_spec or ""
            if format_spec.startswith("{") and format_spec.endswith("}"):
                raise NotImplementedError(
                    "Expressions in format specifiers are not supported"
                )
            parts.append((index, key, format_spec, conversion))
    return tuple(parts)


def from_format(fmt: str, /, *args: object, **kwargs: object) -> Template:
    """
    Parses a format string intended for use with the `str.format()` method and
    returns an equivalent `Template` instance.

    We support *nearly* all the grammatical features of the `str.format()` method,
    including positional arguments with automatic or manual numbering, and
    keyword arguments.

    We also support the limitations of `str.format()`, including lack of support
    for arbitrary expressions in interpolations (these are treated as keys) and
    lack of support for intermingling automatic field numbering with manual field
    numbering.

    The one feature we don't *yet* support is the ability to use interpolations
    inside format specifiers; currently, only literal format specifiers are
    supported. As a result, this throws a NotImplementedError:

        make_template("{:{}}", 42, ".2f")

    There's no fundamental reason we couldn't support this, but it's a bit more
    work, so we haven't done it yet.
    """
    template_args: list[str | Interpolation] = []
    for part in _parse_fmt_string(fmt):
        if isinstance(part, str):
            template_args.append(part)
        else:
            index, key, format_spec, conversion_spec = part
            if index is not None:
                assert key is None
                if index >= len(args):
                    raise IndexError(
                        f"Replacement index {index} out of range for positional args tuple"
                    )
                value = args[index]
                expression = f"args[{index}]"
            else:
                assert key is not None
                if key not in kwargs:
                    raise KeyError(key)
                value = kwargs[key]
                expression = f"kwargs[{key!r}]"
            interpolation = Interpolation(
                value, expression, conversion_spec, format_spec
            )
            template_args.append(interpolation)
    return Template(*template_args)
