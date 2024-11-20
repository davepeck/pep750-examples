"""
Example code to take an old-school format string intended to be used with the
`str.format()` method, and convert it to a modern `Template` instance.
"""

import re
import string
from typing import Literal

from templatelib import Interpolation, Template


def from_format(fmt: str, /, *args: object, **kwargs: object) -> Template:
    """
    Parses a format string intended for use with the `str.format()` method and
    returns an equivalent `Template` instance.

    We support all the features of the `str.format()` method, including
    positional arguments with automatic or manual numbering, keyword arguments,
    interpolations with dot and indexing access, etc.

    We also support the limitations of `str.format()`, including lack of support
    for arbitrary expressions in interpolations (these are treated as keys) and
    lack of support for intermingling automatic field numbering with manual field
    numbering.
    """
    formatter = string.Formatter()
    template_args: list[str | Interpolation] = []
    numbering_mode: Literal["auto", "manual"] | None = None
    auto_index = 0
    for literal_text, field_name, format_spec, conversion in formatter.parse(fmt):
        template_args.append(literal_text)
        if field_name is not None:
            format_spec = format_spec or ""
            if conversion not in {"s", "r", "a", None}:
                raise ValueError(f"Unknown conversion specifier {conversion}")

            if field_name.isdigit():
                if numbering_mode is None:
                    numbering_mode = "manual"
                if numbering_mode != "manual":
                    raise ValueError(
                        "cannot switch from manual field specification to automatic field numbering"
                    )
                key = field_name
            elif not field_name:
                if numbering_mode is None:
                    numbering_mode = "auto"
                if numbering_mode != "auto":
                    raise ValueError(
                        "cannot switch from automatic field numbering to manual field specification"
                    )
                key = str(auto_index)
                auto_index += 1
            else:
                key = field_name
            value, _ = formatter.get_field(key, args, kwargs)

            # Handle nested interpolations in the format spec
            if format_spec and "{" in format_spec:
                format_spec = format_spec.format(*args, **kwargs)

            # CONSIDER: what *is* the most reasonable `expr` to use here?
            template_args.append(Interpolation(value, key, conversion, format_spec))
    return Template(*template_args)
