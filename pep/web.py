from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from typing import Literal, Mapping, Sequence, cast

from . import Interpolation, Template


def _render_str_attribute(key: str, value: str) -> str:
    return f'{key}="{escape(value, quote=True)}"'


def _render_bool_attribute(key: str, value: bool) -> str:
    return key if value else ""


def _render_attribute(key: str, value: str | bool) -> str:
    if isinstance(value, str):
        return _render_str_attribute(key, value)
    return _render_bool_attribute(key, value)


def _render_attributes_dict(d: dict[str, str | bool]) -> str:
    return " ".join(_render_attribute(key, value) for key, value in d.items())


def _render_children(children: Sequence[Element | str]) -> str:
    parts = []
    for child in children:
        if isinstance(child, Element):
            parts.append(str(child))
        else:
            child = escape(child, quote=False)
            parts.append(child)
    return "".join(parts)


@dataclass
class Element:
    """
    A simple representation of an HTML element.

    This makes no attempt to be a full-featured HTML representation or to
    validate the input in any way. It's just a simple data structure that
    can be rendered to a string.
    """

    tag: str  # An empty string represents a fragment
    attributes: dict[str, str | bool]
    children: list["Element | str"]

    @classmethod
    def empty(cls) -> Element:
        return cls("", {}, [])

    @classmethod
    def fragment(cls, children: Sequence[Element | str]) -> Element:
        return cls("", {}, list(children))

    @property
    def is_fragment(self) -> bool:
        return not self.tag

    def __post_init__(self):
        if self.is_fragment and self.attributes:
            raise ValueError("Fragments cannot have attributes, only children")

    def __str__(self) -> str:
        # If there's no tag, render the children directly
        if not self.tag:
            return "".join(str(child) for child in self.children)

        # If there's no children, render the tag directly
        attributes_str = _render_attributes_dict(self.attributes)
        if not self.children:
            if attributes_str:
                return f"<{self.tag} {attributes_str} />"
            return f"<{self.tag} />"

        # Render the tag and children
        children_str = _render_children(self.children)
        if attributes_str:
            return f"<{self.tag} {attributes_str}>{children_str}</{self.tag}>"
        return f"<{self.tag}>{children_str}</{self.tag}>"


class HTMLParseError(Exception):
    pass


class _DebugParser(HTMLParser):
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


class _Parser(HTMLParser):
    root: Element | None
    stack: list[Element]
    in_start_tag: bool

    def __init__(self) -> None:
        super().__init__()
        self.stack = []
        self.root = None
        self.in_start_tag = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.root is not None:
            raise HTMLParseError(
                f"Multiple root elements (starting with {self.root.tag} and finding {tag})"
            )

        def _fix_none(value: str | None) -> str | bool:
            if value is None:
                return True
            return value

        attributes = cast(
            dict[str, str | bool], {key: _fix_none(value) for key, value in attrs}
        )
        element = Element(tag, attributes, [])
        self.stack.append(element)
        self.in_start_tag = False

    def handle_endtag(self, tag: str) -> None:
        element = self.stack.pop()
        if element.tag != tag:
            raise HTMLParseError(f"Unexpected end tag: {tag}")
        if not self.stack:
            self.root = element
        else:
            self.stack[-1].children.append(element)

    def handle_data(self, data: str) -> None:
        # Ignore whitespace (for now)
        data = data.strip()
        if not data:
            return
        if not self.stack:
            raise HTMLParseError(f"Data outside of root element: {data}")
        self.stack[-1].children.append(data)

    def parse_starttag(self, i: int) -> int:
        self.in_start_tag = True
        return super().parse_starttag(i)


def html(template: Template) -> Element:
    """Convert a Template to an Element."""
    parser = _Parser()
    for arg in template.args:
        match arg:
            case str() as s:
                parser.feed(s)
            case Interpolation() as i:
                if isinstance(i.value, dict):
                    if not parser.in_start_tag:
                        raise HTMLParseError("Cannot interpolate dict in HTML content")
                    parser.feed(_render_attributes_dict(i.value))
                elif isinstance(i.value, Element):
                    if parser.in_start_tag:
                        raise HTMLParseError("Cannot interpolate Element in start tag")
                    parser.feed(str(i.value))
                elif isinstance(i.value, Template):
                    if parser.in_start_tag:
                        raise HTMLParseError("Cannot interpolate Template in start tag")
                    result = html(i.value)
                    parser.feed(str(result))
                else:
                    value = i.value
                    assert isinstance(value, str)
                    if parser.in_start_tag:
                        value = escape(value, quote=True)
                        print(f"Escaped value in start tag: {value}")
                    else:
                        value = escape(value, quote=False)
                        print(f"Escaped value NOT in start tag: {value}")
                    parser.feed(value)
    parser.close()
    if not parser.root:
        raise HTMLParseError("No root element")
    return parser.root
