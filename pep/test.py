"""
Test that our implementation of PEP 750, which is currently partially in the
fork of cpython, and partially in the __init__.py in this repository, works.

See the __init__.py for a more detailed explanation.
"""

import pytest
from templatelib import Interpolation, Template

from . import (
    _BUG_CONSTANT_TEMPLATE,
    _MISSING_INTERLEAVING,
    _MISSING_TEMPLATE_ADD_RADD,
    _MISSING_TEMPLATE_EQ,
)

# TODO: replace all instances of *** with "" once both
# _MISSING_INTERLEAVING and _BUG_SINGLE_INTERPOLATION are False


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert template.args == ("",)


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
def test_simple():
    template = t"hello"
    assert isinstance(template, Template)
    assert template.args == ("hello",)


@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
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
    template = t"***{42!a}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].conv == "a"


def test_format_spec():
    template = t"***{42:04d}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].format_spec == "04d"


def test_format_spec_and_conv():
    template = t"***{42!r:04d}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].conv == "r"
    assert template.args[1].format_spec == "04d"


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
def test_add_template_str():
    template = t"hello" + "world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


@pytest.mark.skipif(
    _MISSING_TEMPLATE_ADD_RADD, reason="Template add/radd not implemented"
)
def test_add_template_str_2():
    name = "world"
    template = t"hello {name}!" + " how are you?"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello "
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == name
    assert isinstance(template.args[2], str)
    assert template.args[2] == "!" + " how are you?"


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
def test_add_template_template():
    template = t"hello" + t"world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


@pytest.mark.skipif(
    _MISSING_TEMPLATE_ADD_RADD, reason="Template add/radd not implemented"
)
def test_add_template_template_2():
    name = "world"
    other = "you"
    template = t"hello {name}!" + t" how are {other}?"
    assert isinstance(template, Template)
    assert len(template.args) == 5
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello "
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == name
    assert isinstance(template.args[2], str)
    assert template.args[2] == "!" + " how are "
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == other
    assert isinstance(template.args[4], str)
    assert template.args[4] == "?"


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
def test_add_str_template():
    template = "hello" + t"world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


@pytest.mark.skipif(
    _MISSING_TEMPLATE_ADD_RADD, reason="Template add/radd not implemented"
)
def test_add_str_template_2():
    name = "world"
    template = "hello " + t"there, {name}!"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello " + "there, "
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == name
    assert isinstance(template.args[2], str)
    assert template.args[2] == "!"


# Implicit concat syntax is not supported whatsoever in the current PEP 750
# def test_implicit_concat_str_template():
#     template = "hello" t"world"
#     assert isinstance(template, Template)
#     assert len(template.args) == 1
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello" + "world"


# def test_implicit_concat_template_str():
#     template = t"hello" "world"
#     assert isinstance(template, Template)
#     assert len(template.args) == 1
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello" + "world"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_1():
    assert t"hello" == t"hello"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_2():
    assert t"hello" != t"world"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_3():
    planet = "earth"
    assert t"hello {planet}" == t"hello {planet}"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_4():
    planet = "earth"
    satellite = "moon"
    assert t"hello {planet}" != t"hello {satellite}"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
@pytest.mark.skipif(
    _MISSING_TEMPLATE_ADD_RADD, reason="Template add/radd not implemented"
)
def test_template_eq_5():
    assert "hello" + t" {42}" == t"hello {42}"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_6():
    assert t"hello {42}" + "!" == t"hello {42}!"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_eq_7():
    assert t"{42}" + t"{99}" == t"{42}{99}"


# @pytest.mark.skipif(_BUG_DEBUG_SPECIFIER, reason="Template debug specifier not implemented")
# def test_template_debug_specifier():
#     name = "World"
#     template = t"Hello {name=}"
#     assert template.args[0] == "Hello name="
#     assert template.args[1].value == "World"


def test_template_raw_template_strings_1():
    trade = "shrubberies"
    t = rt'Did you say "{trade}"?\n'
    assert t.args[0] == r'Did you say "'
    assert t.args[2] == r'"?\n'
