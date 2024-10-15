from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
from typing import Any, Literal, Mapping, Sequence, cast

from . import Interpolation, Template


class HTMLParseError(Exception):
    """An error occurred while parsing an HTML template."""

    pass


# ---------------------------------------------------------------------------
# Utility code to render parts of an HTML element
# ---------------------------------------------------------------------------


def _render_str_attribute(key: str, value: str) -> str:
    """Render a string attribute and its untrusted value."""
    return f'{key}="{escape(value, quote=True)}"'


def _render_bool_attribute(key: str, value: bool) -> str:
    """Render a boolean attribute if it's True."""
    return key if value else ""


def _render_attribute(key: str, value: str | bool) -> str:
    """Render an attribute and its value."""
    if isinstance(value, str):
        return _render_str_attribute(key, value)
    return _render_bool_attribute(key, value)


def _render_attributes_mapping(mapping: Mapping[str, str | bool]) -> str:
    """Render a dictionary of attributes."""
    return " ".join(_render_attribute(key, value) for key, value in mapping.items())


def _render_children(children: Sequence[Element | str]) -> str:
    """Render a sequence of children."""
    parts = []
    for child in children:
        if isinstance(child, Element):
            parts.append(str(child))
        else:
            child = escape(child, quote=False)
            parts.append(child)
    return "".join(parts)


# ---------------------------------------------------------------------------
# The main Element class
# ---------------------------------------------------------------------------


@dataclass
class Element:
    """
    A simple representation of an HTML element.

    This makes no attempt to be a full-featured HTML representation or to
    validate the values in any way. It's just a simple data structure that
    can be rendered to a string.
    """

    tag: str  # An empty string represents a fragment
    attributes: dict[str, str | bool]
    children: list["Element | str"]

    @classmethod
    def empty(cls) -> Element:
        """Create an empty element."""
        return cls("", {}, [])

    @classmethod
    def fragment(cls, children: Sequence[Element | str]) -> Element:
        """Create a fragment element (no tag)."""
        return cls("", {}, list(children))

    def __post_init__(self):
        if self.attributes and not self.tag:
            raise ValueError("Fragments cannot have attributes, only children")

    def __str__(self) -> str:
        # If there's no tag, render the children directly
        if not self.tag:
            return _render_children(self.children)

        attributes_str = _render_attributes_mapping(self.attributes)

        # If there's no children, render the tag directly
        if not self.children:
            if attributes_str:
                return f"<{self.tag} {attributes_str} />"
            return f"<{self.tag} />"

        # Render the tag and children
        # TODO handle indentation and pretty-printing
        children_str = _render_children(self.children)
        if attributes_str:
            return f"<{self.tag} {attributes_str}>{children_str}</{self.tag}>"
        return f"<{self.tag}>{children_str}</{self.tag}>"


# ---------------------------------------------------------------------------
# Our custom (but simple) HTML parser
# ---------------------------------------------------------------------------


class _Parser(HTMLParser):
    """
    A simple HTML parser that constructs an Element tree.

    This builds on the standard library's HTMLParser. In a few places,
    it effectively has to "hack" the standard library parser to get the desired
    behavior.

    For a production system, a more robust parser would likely be necessary:
    writing robust template string processing code can be a lot of work!
    """

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
            """Convert None to True for boolean attributes."""
            # Python's HTMLParser uses None to represent boolean attributes,
            # but that's kinda weird. Let's convert it to True.
            return True if value is None else value

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
        # A small hack to allow us to know when we're in a start tag
        # (but not finish parsing it yet)
        self.in_start_tag = True
        return super().parse_starttag(i)


# ---------------------------------------------------------------------------
# Utility code to process HTML template interpolations
# ---------------------------------------------------------------------------


def _process_start_tag_interpolation(value: Any) -> str:
    """
    Process an interpolation value in a start tag.

    Return the string representation of the value to feed to the parser.
    """
    if isinstance(value, Mapping):
        # Render a collection of attributes in a mapping
        return _render_attributes_mapping(value)
    if isinstance(value, str):
        # Escape a value to be used in an attribute
        value = escape(value, quote=True)
        # TODO We currently assume that we're inside an attribute value in
        # the parse, but this may not always be the case.
        return f'"{value}"'
    raise HTMLParseError(
        f"Unsupported start tag interpolation value type: {type(value)}"
    )


def _process_content_interpolation(value: Any) -> str:
    """
    Process an interpolation value outside of a start tag.

    Return the string representation of the value to feed to the parser.
    """
    if isinstance(value, Element):
        # Allow nesting elements in content
        return str(value)
    if isinstance(value, Template):
        # Allow nesting templates in content by first processing them
        # recursively with the html function
        element = html(value)
        return str(element)
    if isinstance(value, str):
        # Escape a value to be used in content
        return escape(value, quote=False)
    raise HTMLParseError(f"Unsupported content interpolation value type: {type(value)}")


# ---------------------------------------------------------------------------
# The main html() template processing function
# ---------------------------------------------------------------------------


def html(template: Template) -> Element:
    """Convert a Template to an Element."""
    parser = _Parser()
    for arg in template.args:
        match arg:
            case str() as s:
                # String content is easy: just continue to parse it as-is
                parser.feed(s)
            case Interpolation() as i:
                # Interpolations are more complex. They can be strings, dicts,
                # Elements, or Templates. It matters *where* in the HTML grammar
                # they appear, so we need to handle each case separately.
                if parser.in_start_tag:
                    value = _process_start_tag_interpolation(i.value)
                else:
                    # TODO what if we're in an end tag?
                    value = _process_content_interpolation(i.value)
                parser.feed(value)
    parser.close()
    if not parser.root:
        raise HTMLParseError("No root element")
    return parser.root
