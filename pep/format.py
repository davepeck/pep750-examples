"""
Example code to take an old-school format string intended to be used with the
`str.format()` method, and convert it to a modern `Template` instance.
"""

import re
from typing import Literal, cast

from templatelib import Interpolation, Template


def make_template_with_eval(s: str, **kwargs: object) -> Template:
    """
    Trivial example of converting something *like* an old-style format string
    into a `Template` using `eval()`.

    This doesn't *quite* support all the features of the `str.format()` method.
    For instance, it does not support positional arguments.

    It also supports some features that are *not* supported by `str.format()`,
    such as arbitrary expressions in the interpolations.

    It's still probably useful in some cases.
    """
    # Replace " with \" but only if it's not preceded by a \
    # already.
    safe = re.sub(r'(?<!\\)"', r'\\"', s)
    to_eval = f't"{safe}"'
    return eval(to_eval, kwargs)


type ParsedIndex = int | None
type ParsedKey = str | None
type ParsedConversion = Literal["a", "r", "s"] | None
type ParsedFormatSpec = str
type ParsedInterpolation = tuple[
    ParsedIndex, ParsedKey, ParsedFormatSpec, ParsedConversion
]


def _parse_fmt_string(fmt: str) -> tuple[str | ParsedInterpolation, ...]:
    # Regular expression to match format specifiers, including conversion and format spec
    # pattern = re.compile(r"(.*?)\{([^\{\}]*?)(?:!([sra]))?(?::([^\{\}]*?))?\}")
    pattern = re.compile(
        r"(.*?)\{([^\{\}]*?)(?:!([sra]))?(?::((?:[^\{\}]|\{[^\{\}]*\})*))?\}"
    )

    pos = 0
    current_index = 0
    numbering_mode: Literal["auto", "manual"] | None = None
    result: list[str | ParsedInterpolation] = []

    for match in pattern.finditer(fmt):
        start, end = match.span()

        # Add the preceding static string part, if any
        if pos < start:
            result.append(fmt[pos:start])

        # Extract the parts
        static_string = match.group(1)
        key = match.group(2)
        conversion_spec = match.group(3)
        format_spec = match.group(4)

        # Ensure the types are correct
        assert isinstance(static_string, str)
        assert isinstance(key, str)
        assert isinstance(conversion_spec, str) or conversion_spec is None
        assert isinstance(format_spec, str) or format_spec is None

        if not conversion_spec:
            conversion_spec = None

        if conversion_spec not in {None, "a", "r", "s"}:
            raise ValueError(f"Unknown conversion specifier: {conversion_spec}")

        if format_spec is None:
            format_spec = ""

        # TODO we can definitely implement this in the future. But for now: why?
        if format_spec and format_spec.startswith("{") and format_spec.endswith("}"):
            raise NotImplementedError("Format spec interpolations are not supported")

        # The regex will not match invalid conversion specifiers; they will
        # end up in the key part. So we need to check for them here.
        if "!" in key:
            maybe_spec = key.split("!", maxsplit=1)[-1]
            raise ValueError(f"Unknown conversion specifier: {maybe_spec}")

        # Add the static string part from the match
        if static_string:
            result.append(static_string)

        # Decide what kind of key this is. There are three possibilities:
        #
        # 1. An implicit index, e.g. "{}"
        # 2. An explicit index, e.g. "{3}"
        # 3. A key, e.g. "{name}" or "{0 + 1}"

        if not key:
            # This is an implicit index. Make sure we're in auto-numbering mode
            # *or* move us *to* auto-numbering mode if we're not in manual mode.
            if numbering_mode == "manual":
                raise ValueError(
                    "cannot switch from automatic field numbering to manual field specification"
                )
            numbering_mode = "auto"
            index = current_index
            current_index += 1
            key = None
        elif key.isdigit():
            # This is an explicit index
            if numbering_mode == "auto":
                raise ValueError(
                    "cannot switch from automatic field numbering to manual field specification"
                )
            numbering_mode = "manual"
            index = int(key)
            key = None
        else:
            # This is a key
            index = None

        # Append it.
        result.append((index, key, format_spec, conversion_spec))

        pos = end

    # Add any remaining static string part
    if pos < len(fmt):
        result.append(fmt[pos:])

    return tuple(result)


def make_template(fmt: str, /, *args: object, **kwargs: object) -> Template:
    """
    Sophisticated example of converting an old-style format string to a `Template`
    by directly parsing the string.

    We support *nearly* all the grammatical features of the `str.format()` method,
    including positional arguments with automatic or manual numbering, and
    keyword arguments.

    We also support the limitations of `str.format()`, including lack of support
    for arbitrary expressions in interpolations (these are treated as keys) and
    lack of support for intermingling automatic field numbering with manual field
    numbering.

    The one feature we don't *yet* support is the ability to use interpolations
    for format specifiers; only literal format specifiers are supported.
    As a result, this currently throws a NotImplementedError:

        make_template("{:{}}", 42, ".2f")

    There's no fundamental reason we couldn't support this, but it's a bit more
    complicated, so we haven't done it yet.
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
