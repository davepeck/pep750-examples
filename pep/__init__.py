"""
Examples for PEP 750.

This repository has a .devcontainer and a Dockerfile that pulls down a fork
of Python 3.14 that supports an *older* version of the PEP 750 specification.

We smooth over the differences here by defining the *current* PEP 750's
`Template` and `Interpolation` types. We also implement the `t` prefix here.

To *use* the `t` prefix as described in the current version of PEP 750, simply:

from . import t

name = "World"
template = t"Hello {name}"

When our fork of cpython is updated, we'll also remove all this stuff -- again,
it exists only temporarily, to smooth over differences between the old PEP 750
spec and the new.
"""

from typing import (
    Any,
    Sequence,
    Literal,
    Interpolation as OldVersionOfInterpolation,
)
from dataclasses import dataclass


@dataclass(frozen=True, match_args=True)
class Interpolation:
    value: Any
    expr: str
    format_spec: str = ""
    conv: Literal["a", "r", "s"] | None = None


@dataclass(frozen=True, match_args=True)
class Template:
    args: Sequence[str | Interpolation]



def t(*args: str | OldVersionOfInterpolation) -> Template:
    """
    Implement the proposed PEP 750 template string behavior, using the
    older cpython implementation of tagged strings.

    See test_tstring.py for examples of the expected behavior.
    """

    eo_args: list[str | Interpolation] = []
    last_was_str: bool = False

    for arg in args:
        if isinstance(arg, OldVersionOfInterpolation):
            if not last_was_str:
                eo_args.append("")
            print(arg)
            # Work around a bug in the current reference implementation of
            # PEP 750. Specifically, it doesn't always set the OldInterpolation.conv
            # and OldInterpolation.format_spec attributes correctly:
            #
            # def args(*args):
            #     return args
            #
            # Correct:
            # >>> args"{42!r}"
            # (InterpolationConcrete(getvalue=<function <interpolation> at 0xffff9341d850>, expr='42', conv='r', format_spec=None),)
            #
            # BUG:
            # >>> args"{42:.2f}"
            # (InterpolationConcrete(getvalue=<function <interpolation> at 0xffff9341d640>, expr='42', conv='.2f', format_spec=None),)
            #
            # Correct:
            # >>> args"{42!r:.2f}"
            # (InterpolationConcrete(getvalue=<function <interpolation> at 0xffff9341d850>, expr='42', conv='r', format_spec='.2f'),)
            #
            # The workaround here will work *unless* there's no conv and the
            # format_spec happens to be exactly "a", "r", or "s". In that case,
            # we will incorrectly interpret the format_spec as the conv. Oh well for now!
            #
            # -Dave

            conv = None
            format_spec = ""

            if arg.conv is not None:
                if arg.conv in ("a", "r", "s"):
                    conv = arg.conv
                    format_spec = arg.format_spec or ""
                else:
                    format_spec = arg.conv

            value_interpolation = Interpolation(arg.getvalue(), arg.expr, format_spec, conv)  # type: ignore
            eo_args.append(value_interpolation)
            last_was_str = False
        else:
            eo_args.append(arg)
            last_was_str = True

    if not last_was_str:
        eo_args.append("")

    assert len(eo_args) >= 1
    assert len(eo_args) % 2 == 1

    return Template(tuple(eo_args))

