"""Examples for PEP 750. See README.md for details."""

from html.parser import HTMLParser

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
