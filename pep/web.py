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


@dataclass(frozen=True)
class Element:
    """
    A simple representation of an HTML element.

    This makes no attempt to be a full-featured HTML representation, to be
    performant, or to validate the presence of attributes or children in
    any way. Instead, it's a simple data structure that can be rendered to
    a string.

    Hopefully it's a useful starting point for thinking about how to build
    a more robust HTML templating system.
    """

    tag: str  # An empty string indicates a fragment
    attributes: Mapping[str, str | bool]
    children: Sequence["Element | str"]

    @classmethod
    def empty(cls) -> Element:
        """Create an empty element."""
        return cls("", {}, [])

    @classmethod
    def fragment(cls, children: Sequence[Element | str]) -> Element:
        """Create a fragment element (empty tag)."""
        return cls("", {}, list(children))

    def __post_init__(self):
        """Validate the element after it's been created."""
        if self.attributes and not self.tag:
            raise ValueError("Fragments cannot have attributes, only children")

    def append(self, child: Element | str) -> Element:
        """Append a child to the element."""
        return Element(self.tag, self.attributes, list(self.children) + [child])

    def __str__(self) -> str:
        """Render the element to an HTML string."""
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
    A simple HTML parser that constructs a tree of `Element`s.

    This builds on the Python standard library's HTMLParser. This is fine for
    our example purposes, but not perfect: we have to work around some of the
    limitations of the parser (mostly, by overriding interal methods and
    using internal state) in order to support our desired template string
    syntax.

    A production system would need a more robust parser, but that's potentially
    a lot of work! Hopefully this is a useful starting point for thinking about
    how to build a more robust HTML templating system.
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
            raise HTMLParseError(f"Multiple root elements ({self.root.tag} and {tag})")

        def _none_to_true(value: str | None) -> str | bool:
            """Convert None to True for boolean attributes."""
            # Python's HTMLParser uses None to represent boolean attributes,
            # but that's kinda weird. Let's convert it to True.
            return True if value is None else value

        attributes = {key: _none_to_true(value) for key, value in attrs}
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
            self.stack[-1] = self.stack[-1].append(element)

    def handle_data(self, data: str) -> None:
        # Ignore whitespace entirely for now
        # TODO handle whitespace in a more sophisticated way
        data = data.strip()
        if not data:
            return
        if not self.stack:
            raise HTMLParseError(f"Data outside of root element: {data}")
        self.stack[-1] = self.stack[-1].append(data)

    def parse_starttag(self, i: int) -> int:
        # A small hack to allow us to know when we're in a start tag
        # (but haven't finished parsing it yet)
        # TODO: just how accurate is this? Is there a better way?
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
    raise HTMLParseError(f"Unsupported start tag interpolation: {type(value)}")


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
    # TODO support "component" interpolations: callables that take
    # the attributes and children and return an Element for rendering
    raise HTMLParseError(f"Unsupported content interpolation: {type(value)}")


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
