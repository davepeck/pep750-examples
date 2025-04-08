from typing import Mapping, Sequence

import pytest
from string.templatelib import Template

from . import _BUG_CONSTANT_TEMPLATE
from .web import Element, HTMLParseError, html

# ---------------------------------------------------------------------------
# Tests for the Element class (mostly, its __str__ method)
# ---------------------------------------------------------------------------


def test_empty_element():
    element = Element.empty()
    assert str(element) == ""


def test_empty_fragment():
    element = Element.fragment([])
    assert str(element) == ""


def test_fragment_with_text_children():
    element = Element.fragment(["Hello", "world"])
    assert str(element) == "Helloworld"


def test_fragment_children_escape():
    element = Element.fragment(["<script>alert('evil')</script>"])
    assert str(element) == "&lt;script&gt;alert('evil')&lt;/script&gt;"


def test_fragment_with_element_children():
    element = Element.fragment(
        [Element("p", {}, ["hello"]), Element("p", {}, ["world"])]
    )
    assert str(element) == "<p>hello</p><p>world</p>"


def test_fragment_nesting():
    fragment = Element.fragment(
        [Element("p", {}, ["hello"]), Element("p", {}, ["world"])]
    )
    element = Element("div", {}, [Element("p", {}, ["wow"]), fragment])
    assert str(element) == "<div><p>wow</p><p>hello</p><p>world</p></div>"


def test_invalid_fragment():
    with pytest.raises(ValueError):
        _ = Element("", {"class": "greeting"}, [])


def test_element_with_no_children():
    element = Element("div", {}, [])
    assert str(element) == "<div />"


def test_element_with_attributes():
    element = Element("div", {"class": "greeting"}, [])
    assert str(element) == '<div class="greeting" />'


def test_element_with_text_children():
    element = Element("div", {}, ["Hello", "world"])
    assert str(element) == "<div>Helloworld</div>"


def test_element_with_text_children_and_attributes():
    element = Element("div", {"class": "greeting"}, ["Hello", "world"])
    assert str(element) == '<div class="greeting">Helloworld</div>'


def test_element_attribute_escape():
    element = Element("div", {"class": 'greeting" onclick="alert("hi")'}, [])
    assert (
        str(element)
        == '<div class="greeting&quot; onclick=&quot;alert(&quot;hi&quot;)" />'
    )


def test_element_child_str_escape():
    element = Element("div", {}, ['<script>alert("evil")</script>'])
    assert str(element) == '<div>&lt;script&gt;alert("evil")&lt;/script&gt;</div>'


# ---------------------------------------------------------------------------
# Tests for the html() template processing function
# ---------------------------------------------------------------------------


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_empty():
    template: Template = t""
    with pytest.raises(HTMLParseError):
        element = html(template)


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_only_text():
    template: Template = t"Hello, world!"
    with pytest.raises(HTMLParseError):
        element = html(template)


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_self_closing_tag():
    template: Template = t"<br />"
    element = html(template)
    expected = Element("br", {}, [])
    assert element == expected


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_simple_p():
    template: Template = t"<p>Hello, world!</p>"
    element = html(template)
    expected = Element("p", {}, ["Hello, world!"])
    assert element == expected


def test_html_p_text_interpolation():
    text = "Hello, world!"
    template: Template = t"<p>{text}</p>"
    element = html(template)
    expected = Element("p", {}, ["Hello, world!"])
    assert element == expected


def test_html_p_text_interpolation_escape():
    evil = "<script>alert('evil')</script>"
    template: Template = t"<p>{evil}</p>"
    element = html(template)
    expected = Element("p", {}, ["<script>alert('evil')</script>"])
    assert element == expected


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_nested_safe_text():
    good = html(t"<script>alert('good')</script>")
    template: Template = t"<p>{good}</p>"
    element = html(template)
    expected = Element("p", {}, [Element("script", {}, ["alert('good')"])])
    assert element == expected


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_nested_template_text():
    good = t"<script>alert('good')</script>"
    template: Template = t"<p>{good}</p>"
    element = html(template)
    expected = Element("p", {}, [Element("script", {}, ["alert('good')"])])


def test_html_p_with_attributes():
    text = 'Hello, "world!"'
    template: Template = t'<p class="greeting">{text}</p>'
    element = html(template)
    expected = Element("p", {"class": "greeting"}, ['Hello, "world!"'])
    assert element == expected


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_nested_elements():
    template: Template = t"<div><p>Hello, world!</p></div>"
    element = html(template)
    expected = Element("div", {}, [Element("p", {}, ["Hello, world!"])])
    assert element == expected


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant template bug")
def test_html_many_nested_elements():
    template: Template = t"""
    <div>
        Raw text
        <p>Hello, world!</p>
        <ul>
            <li>One</li>
            <li>Two</li>
            <li>Three</li>
        </ul>
    </div>
    """
    element = html(template)
    expected = Element(
        "div",
        {},
        [
            "Raw text",
            Element("p", {}, ["Hello, world!"]),
            Element(
                "ul",
                {},
                [
                    Element("li", {}, ["One"]),
                    Element("li", {}, ["Two"]),
                    Element("li", {}, ["Three"]),
                ],
            ),
        ],
    )
    assert element == expected


def test_html_attribute_str_interploation():
    cls = 'gree"tin"g'
    text = "Hello, world!"
    template: Template = t"<p class={cls}>{text}</p>"
    element = html(template)
    expected = Element("p", {"class": 'gree"tin"g'}, ["Hello, world!"])
    assert element == expected


def test_html_attribute_dict_interpolation():
    attributes = {"class": "greeting", "data-foo": None}
    text = "Hello, world!"
    template: Template = t"<p {attributes}>{text}</p>"
    element = html(template)
    expected = Element("p", {"class": "greeting", "data-foo": None}, ["Hello, world!"])
    assert element == expected


def test_html_dict_interpolation_not_allowed_in_content():
    attributes = {"class": "greeting"}
    template: Template = t"<p>{attributes}</p>"
    with pytest.raises(HTMLParseError):
        element = html(template)


def test_html_tag_interpolation():
    tag = "p"
    text = "Hello, world!"
    template: Template = t"<{tag}>{text}</{tag}>"
    element = html(template)
    expected = Element("p", {}, ["Hello, world!"])
    assert element == expected


def test_html_tag_callable_interpolation():
    def Magic(
        attributes: Mapping[str, str | None], children: Sequence[str | Element]
    ) -> Element:
        """A simple, but extremely magical, component."""
        magic_attributes = {**attributes, "data-magic": "yes"}
        magic_children = [*children, "Magic!"]
        return Element("div", magic_attributes, magic_children)

    template: Template = t'<{Magic} id="wow"><b>FUN!</b></{Magic}>'
    element = html(template)
    expected = Element(
        "div",
        {"id": "wow", "data-magic": "yes"},
        [Element("b", {}, ["FUN!"]), "Magic!"],
    )
    assert element == expected
