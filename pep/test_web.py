import pytest
from deepdiff import DeepDiff

from . import Template, t
from .web import Element, HTMLParseError, html

#
# Tests for Element.__str__()
#


def test_empty_element():
    element = Element("", {}, [])
    assert str(element) == ""


def test_empty_fragment():
    element = Element.fragment([])
    assert str(element) == ""


def test_fragment_with_text_children():
    element = Element.fragment(["Hello", "world"])
    assert str(element) == "Helloworld"


def test_element_with_no_children():
    element = Element("div", {}, [])
    assert str(element) == "<div />"


#
# Tests for html()
#


def test_html_empty():
    template: Template = t""
    with pytest.raises(HTMLParseError):
        element = html(template)


def test_html_only_text():
    template: Template = t"Hello, world!"
    with pytest.raises(HTMLParseError):
        element = html(template)


def test_html_self_closing_tag():
    template: Template = t"<br />"
    element = html(template)
    expected = Element("br", {}, [])
    assert element == expected


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


def test_html_p_with_attributes():
    text = "Hello, world!"
    template: Template = t'<p class="greeting">{text}</p>'
    element = html(template)
    expected = Element("p", {"class": "greeting"}, ["Hello, world!"])
    assert element == expected


def test_html_nested_elements():
    template: Template = t"<div><p>Hello, world!</p></div>"
    element = html(template)
    expected = Element("div", {}, [Element("p", {}, ["Hello, world!"])])
    assert element == expected


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
    diff = DeepDiff(element, expected)
    assert not diff, f"Output differs:\n{diff}"


def test_html_attribute_str_interploation():
    cls = "greeting"
    text = "Hello, world!"
    template: Template = t"<p class={cls}>{text}</p>"
    element = html(template)
    expected = Element("p", {"class": "greeting"}, ["Hello, world!"])


def test_html_attribute_dict_interpolation():
    attributes = {"class": "greeting", "data-foo": True}
    text = "Hello, world!"
    template: Template = t"<p {attributes}>{text}</p>"
    element = html(template)
    expected = Element("p", {"class": "greeting", "data-foo": True}, ["Hello, world!"])
    assert element == expected


def test_html_dict_interpolation_not_allowed_in_content():
    attributes = {"class": "greeting"}
    template: Template = t"<p>{attributes}</p>"
    with pytest.raises(HTMLParseError):
        element = html(template)