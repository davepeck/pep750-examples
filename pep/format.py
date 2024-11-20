"""
Example code to take an old-school format string intended to be used with the
`str.format()` method, and convert it to a modern `Template` instance.
"""

import re
import string
from typing import Literal

from templatelib import Interpolation, Template


def _split_field_name(field_name: str) -> tuple[str, str]:
    """
    Splits a field name into a key and a rest.

    The key is the part before the first dot or open bracket. The rest is the
    part after the first dot or open bracket.

    If there is no dot or open bracket, the rest is an empty string.
    """
    # str.format() field names can be simple:
    #
    # 1. A number, which is a positional argument.
    # 2. A name, which is a keyword argument.
    # 3. Empty, which is an automatic field number.
    #
    # They can then tack on arbitrary indexing and attribute access:
    #
    # 1. .name accesses an attribute.
    # 2. [name] accesses an item.
    #
    # We call the simple part the "key", and the indexing and attribute
    # access the "rest".

    first_dot = field_name.find(".")
    first_open_brace = field_name.find("[")
    if first_dot == -1 and first_open_brace == -1:
        return field_name, ""
    if first_dot == -1:
        return field_name[:first_open_brace], field_name[first_open_brace:]
    if first_open_brace == -1:
        return field_name[:first_dot], field_name[first_dot:]
    if first_dot < first_open_brace:
        return field_name[:first_dot], field_name[first_dot:]
    assert first_open_brace < first_dot
    return field_name[:first_open_brace], field_name[first_open_brace:]


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

            field_key, rest = _split_field_name(field_name)

            # If field_key is a number, or is empty, support manual and automatic
            # field numbering.
            if field_key.isdigit():
                if numbering_mode is None:
                    numbering_mode = "manual"
                if numbering_mode != "manual":
                    raise ValueError(
                        "cannot switch from manual field specification to automatic field numbering"
                    )
            elif not field_key:
                if numbering_mode is None:
                    numbering_mode = "auto"
                if numbering_mode != "auto":
                    raise ValueError(
                        "cannot switch from automatic field numbering to manual field specification"
                    )
                field_key = str(auto_index)
                auto_index += 1

            # Recompose the field name with numbering mode taken into account
            final_field = field_key + rest
            value, _ = formatter.get_field(final_field, args, kwargs)

            # Handle nested interpolations in the format spec
            if format_spec and "{" in format_spec:
                format_spec = format_spec.format(*args, **kwargs)

            # CONSIDER: what *is* the most reasonable `expr` to use here?
            # for now, just use `final_field`, even though it is not
            # necessarily a valid Python expression.
            template_args.append(
                Interpolation(value, final_field, conversion, format_spec)
            )
    return Template(*template_args)
