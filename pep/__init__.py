"""Examples for PEP 750. See README.md for details."""

from html.parser import HTMLParser

#
# Known bugs/divergences between cpython/tstrings and the current PEP 750 spec
#

# When these go to False, we can remove 'em.

_BUG_CONSTANT_TEMPLATE = True
"""True if constant templates are turned into Constant in the cpython prototype."""

_MISSING_TEMPLATE_ADD_RADD = True
"""True if the cpython prototype is missing __add__ and __radd__ for Template."""

_MISSING_TEMPLATE_EQ = True
"""True if the cpython prototype is missing an updated __eq__ for Template."""

_MISSING_INTERLEAVING = True
"""True if the cpython prototype doesn't interleave strings and interpolations."""

_MISSING_IMPLICIT_CONCAT = True
"""True if the cpython prototype doesn't support implicit concatenatenation."""

_INCORRECT_INIT_ARGS = True
"""True if the cpython prototype doesn't have the correct __init__ arguments."""

_BUG_SINGLE_INTERPOLATION_OUTSIDE_OF_TEMPLATE = True
"""True if the cpython prototype evaluates `t"{42}"` as Interpolation(...), not Template."""

_BUG_INTERPOLATION_MATCH_ARGS = True
"""True if the cpython prototype doesn't match the PEP 750 spec for Interpolation.__match_args__."""


#
# Debug utilities -- useful when developing some of these examples
#


class _DebugParser(HTMLParser):
    """
    Parser that prints debug information about the HTML it's parsing.

    Useful for learning how python's standard HTMLParser works.
    """

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        print(f"starttag: {tag} {attrs}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        print(f"startendtag: {tag} {attrs}")

    def handle_endtag(self, tag: str) -> None:
        print(f"endtag: {tag}")

    def handle_data(self, data: str) -> None:
        print(f"Data: {data}")

    def parse_starttag(self, i: int) -> int:
        response = super().parse_starttag(i)
        print(f"parse_starttag: {i} -> {response}")
        return response
