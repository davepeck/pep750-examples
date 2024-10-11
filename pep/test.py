"""
Test that our implementation of PEP 750, which is currently partially in the
fork of cpython, and partially in the __init__.py in this repository, works.

See the __init__.py for a more detailed explanation.
"""

from . import t, Template, Interpolation


def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert template.args == ("",)

def test_simple():
    template = t"hello"
    assert isinstance(template, Template)
    assert template.args == ("hello",)

def test_only_interpolation():
    template = t"{42}"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert isinstance(template.args[2], str)
    assert template.args[2] == ""

def test_mixed():
    v = 99
    template = t"hello{42}world{v}goodbye"
    assert isinstance(template, Template)
    assert len(template.args) == 5
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello"
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert isinstance(template.args[2], str)
    assert template.args[2] == "world"
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == v
    assert isinstance(template.args[4], str)
    assert template.args[4] == "goodbye"

def test_conv():
    template = t"{42!a}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].conv == "a"


def test_format_spec():
    template = t"{42:04d}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].format_spec == "04d"
