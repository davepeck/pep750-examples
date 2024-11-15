"""
Test that our implementation of PEP 750, which is currently partially in the
fork of cpython, and partially in the __init__.py in this repository, works.

See the __init__.py for a more detailed explanation.
"""

import asyncio

import pytest
from templatelib import Interpolation, Template

from . import (
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    _BUG_CONSTANT_TEMPLATE,
    _BUG_DEBUG_SPECIFIER,
    _BUG_DEBUG_SPECIFIER_WITH_FMT,
    _BUG_INTERPOLATION_CONSTRUCTOR_SEGFAULT,
    _BUG_MANY_EXPRESSIONS,
    _BUG_NESTED_FORMAT_SPEC,
    _BUG_TEMPLATE_CONSTRUCTOR,
    _INCORRECT_SYNTAX_ERROR_MESSAGE,
    _MISSING_INTERLEAVING,
    _MISSING_TEMPLATE_ADD_RADD,
    _MISSING_TEMPLATE_EQ,
    _MISSING_TEMPLATE_HASH,
)


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert template.args == ("",)  # This will fail if interleaving is not implemented


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


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
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


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
def test_format_spec_and_conv():
    template = t"{42!r:04d}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].conv == "r"
    assert template.args[1].format_spec == "04d"


@pytest.mark.skipif(
    _BUG_NESTED_FORMAT_SPEC, reason="Nested format specs not implemented"
)
def test_format_spec_with_interpolation():
    value = 42
    precision = 2
    template = t"Value: {value:.{precision}f}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].format_spec == ".2f"


@pytest.mark.skipif(_BUG_CONSTANT_TEMPLATE, reason="Constant templates bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_add_template_str():
    template = t"hello" + "world"
    assert isinstance(template, Template)
    assert len(template.args) == 1, f"len(template.args) == {len(template.args)}"
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
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
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
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
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


def test_interpolation_constructor_1():
    i1 = Interpolation(42, "i1")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv is None
    assert i1.format_spec == ""


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
def test_interpolation_constructor_2():
    i1 = Interpolation(42, "i1", "a")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv == "a"
    assert i1.format_spec == ""


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
def test_interpolation_constructor_3():
    i1 = Interpolation(42, "i1", "a", ",.2f")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv == "a"
    assert i1.format_spec == ",.2f"


def test_interpolation_constructor_kwargs_1():
    i1 = Interpolation(value=42, expr="i1")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv is None
    assert i1.format_spec == ""


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
def test_interpolation_constructor_kwargs_2():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expr="i1", conv="a")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv == "a"
    assert i1.format_spec == ""


def test_interpolation_constructor_kwargs_3():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expr="i1", format_spec=",.2f")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv == None
    assert i1.format_spec == ",.2f"


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
def test_interpolation_constructor_kwargs_4():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expr="i1", conv="a", format_spec=",.2f")
    assert i1.value == 42
    assert i1.expr == "i1"
    assert i1.conv == "a"
    assert i1.format_spec == ",.2f"


@pytest.mark.skipif(_BUG_INTERPOLATION_CONSTRUCTOR_SEGFAULT, reason="Segfault bug")
def test_interpolation_constructor_invalid_1():
    with pytest.raises(TypeError):
        _ = Interpolation(42)


@pytest.mark.skipif(_BUG_INTERPOLATION_CONSTRUCTOR_SEGFAULT, reason="Segfault bug")
def test_interpolation_constructor_invalid_2():
    with pytest.raises(TypeError):
        # expr must be a string
        _ = Interpolation(42, None)


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
@pytest.mark.skipif(_BUG_INTERPOLATION_CONSTRUCTOR_SEGFAULT, reason="Segfault bug")
def test_interpolation_constructor_invalid_3():
    with pytest.raises(ValueError):
        # conv must be one of 'a', 'r', 's' or None
        _ = Interpolation(42, "i1", "bogus")


@pytest.mark.skipif(_BUG_INTERPOLATION_CONSTRUCTOR_SEGFAULT, reason="Segfault bug")
def test_interpolation_constructor_invalid_kwargs_1():
    with pytest.raises(TypeError):
        # No such kwarg
        _ = Interpolation(whatever=42)


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
def test_template_constructor_invalid():
    # Only str and Interpolation objects are allowed in the constructor
    with pytest.raises(TypeError):
        _ = Template(42)


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_empty():
    # PEP 750 requires that `Template.args` contains one more string than
    # interpolations. If there are no interpolations, we must therefore have
    # one empty string. `Template.args` can never be empty.
    template = Template()
    expected = ("",)
    assert template.args == expected


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_single_string():
    template = Template("hello")
    expected = ("hello",)
    assert template.args == ("hello",)


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_neighboring_strings():
    template = Template("hello", "world")
    expected = ("helloworld",)
    assert template.args == expected


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_single_interpolation():
    i1 = Interpolation(42, "i1", None, "")
    template = Template(i1)
    expected = ("", i1, "")
    assert template.args == expected


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_neighboring_interpolations():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    template = Template(i1, i2)
    expected = ("", i1, "", i2, "")
    assert template.args == expected


@pytest.mark.skipif(_BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor bug")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_constructor_interleaving_all_the_things():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    i3 = Interpolation(100, "i3", None, "")
    i4 = Interpolation(101, "i4", None, "")
    template = Template("hello", "there", i1, i2, "wow", "neat", i3, "fun", i4)
    expected = (
        "hellothere",
        i1,
        "",
        i2,
        "wowneat",
        i3,
        "fun",
        i4,
        "",
    )
    assert template.args == expected


# TODO uncomment these when _MISSING_IMPLICIT_CONCAT is False

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


# def test_implicit_concat_fstr_template():
#     name = "world"
#     template = f"hello {name}, " t"your name is {name}!"
#     assert isinstance(template, Template)
#     assert len(template.args) == 5
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello "
#     assert isinstance(template.args[1], Interpolation)
#     assert template.args[1].value == name
#     assert isinstance(template.args[2], str)
#     assert template.args[2] == ", " + "your name is "
#     assert isinstance(template.args[3], Interpolation)
#     assert template.args[3].value == name
#     assert isinstance(template.args[4], str)
#     assert template.args[4] == "!"


# def test_implicit_concat_template_fstr():
#     name = "world"
#     template = t"hello {name}, " f"your name is {name}!"
#     assert isinstance(template, Template)
#     assert len(template.args) == 5
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello "
#     assert isinstance(template.args[1], Interpolation)
#     assert template.args[1].value == name
#     assert isinstance(template.args[2], str)
#     assert template.args[2] == ", " + "your name is "
#     assert isinstance(template.args[3], Interpolation)
#     assert template.args[3].value == name
#     assert isinstance(template.args[4], str)
#     assert template.args[4] == "!"


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


@pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
def test_template_hash_1():
    assert hash(t"hello") == hash(t"hello")


@pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
def test_template_hash_2():
    planet = "earth"
    assert hash(t"hello {planet}") == hash(t"hello {planet}")


@pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
def test_template_hash_3():
    assert hash("hello" + t" {42}") == hash(t"hello {42}")


@pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
def test_template_hash_fails_if_values_are_not_hashable():
    with pytest.raises(TypeError):
        _ = hash(t"hello {[]}")


# Testing that hashes *aren't* equal seems problematic to me? Commenting out for now. -Dave
#
# @pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
# def test_template_hash_4():
#     assert hash(t"hello") != hash(t"world")
#
# @pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
# def test_template_hash_5():
#     planet = "earth"
#     satellite = "moon"
#     assert hash(t"hello {planet}") != hash(t"hello {satellite}")


@pytest.mark.skipif(_MISSING_TEMPLATE_HASH, reason="Template hash not implemented")
def test_template_hash_6():
    tup = (1, 2, 3)
    try:
        hash(t"Tuple: {tup}")
    except TypeError:
        pytest.fail("Should not raise TypeError for hashable values")


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
@pytest.mark.skipif(
    _BUG_DEBUG_SPECIFIER, reason="Template debug specifier not implemented"
)
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_debug_specifier():
    name = "World"
    template = t"Hello {name=}"
    assert template.args[0] == "Hello name="
    assert template.args[1].value == "World"
    assert template.args[1].conv == "r"


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
@pytest.mark.skipif(
    _BUG_DEBUG_SPECIFIER, reason="Template debug specifier not implemented"
)
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_template_debug_specifier_expr_preserves_whitespace():
    name = "World"
    template = t"Hello {   name  = }"
    assert template.args[0] == "Hello    name  = "
    assert template.args[1].value == "World"
    assert template.args[1].conv == "r"


@pytest.mark.skipif(
    __BUG_INTERPOLATION_CONSTRUCTOR_IGNORE_CONV,
    reason="Interpolation constructor conv bug",
)
@pytest.mark.skipif(
    _BUG_DEBUG_SPECIFIER, reason="Template debug specifier not implemented"
)
@pytest.mark.skipif(
    _BUG_DEBUG_SPECIFIER_WITH_FMT,
    reason="Template debug specifier with fmt string not implemented",
)
def test_template_debug_specifier_with_format_spec():
    value = 42
    template = t"Value: {value=:spec}"
    assert template.args[0] == "Value: value="
    assert template.args[1].value == 42
    assert template.args[1].conv == "s"
    assert template.args[1].format_spec == "spec"


def test_template_raw_template_strings_1():
    trade = "shrubberies"
    t = rt'Did you say "{trade}"?\n'
    assert t.args[0] == r'Did you say "'
    assert t.args[2] == r'"?\n'


@pytest.mark.skipif(
    _INCORRECT_SYNTAX_ERROR_MESSAGE,
    reason="Template syntax error message not implemented",
)
def test_syntax_error_1():
    with pytest.raises(
        SyntaxError, match="t-string: valid expression required before '}'"
    ):
        # Use exec to avoid syntax error in the test itself
        exec('t"hello {}"')
        # Now, we got "f-string: valid expression required before '}'"


@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_nested_interpolation():
    """Test nested interpolations with correct interleaving"""
    name = "World"
    greeting = "Hello"
    template = t"{greeting} {t'{name}'}"
    assert isinstance(template, Template)
    assert len(template.args) == 5
    assert isinstance(template.args[0], str)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == "Hello"
    assert isinstance(template.args[2], str)
    assert template.args[2] == " "
    assert isinstance(template.args[3], Interpolation)
    assert isinstance(template.args[3].value, Template)
    assert isinstance(template.args[4], str)
    assert template.args[4] == ""


@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_multiple_adjacent_interpolations():
    """Test multiple adjacent interpolations with correct interleaving"""
    x, y = 10, 20
    template = t"{x}{y}{x + y}"
    assert isinstance(template, Template)
    assert len(template.args) == 7
    assert isinstance(template.args[0], str)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 10
    assert isinstance(template.args[2], str)
    assert template.args[2] == ""
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == 20
    assert isinstance(template.args[4], str)
    assert template.args[4] == ""
    assert isinstance(template.args[5], Interpolation)
    assert template.args[5].value == 30
    assert isinstance(template.args[6], str)
    assert template.args[6] == ""


@pytest.mark.skipif(_BUG_NESTED_FORMAT_SPEC, reason="Interleaving not implemented")
@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_format_spec_with_interpolation():
    """Test format specifications with nested interpolations"""
    width = 10
    value = 42
    template = t"{value:.{width}f}"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].format_spec == ".10f"
    assert isinstance(template.args[2], str)
    assert template.args[2] == ""


@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_complex_expressions_with_interleaving():
    """Test complex expressions maintaining interleaving"""
    x, y = 10, 20
    template = t"Result: {x * y} and {sum([1, 2, 3])}"
    assert isinstance(template, Template)
    assert len(template.args) == 5
    assert isinstance(template.args[0], str)
    assert template.args[0] == "Result: "
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 200
    assert isinstance(template.args[2], str)
    assert template.args[2] == " and "
    assert isinstance(template.args[3], Interpolation)
    assert template.args[3].value == 6
    assert isinstance(template.args[4], str)
    assert template.args[4] == ""


def test_unicode_with_interleaving():
    """Test Unicode strings with correct interleaving"""
    name = "世界"
    template = t"こんにちは{name}さん👋"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == "こんにちは"
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == "世界"
    assert isinstance(template.args[2], str)
    assert template.args[2] == "さん👋"


@pytest.mark.skipif(_MISSING_INTERLEAVING, reason="Interleaving not implemented")
def test_raw_template_with_interleaving():
    """Test raw template strings maintain correct interleaving"""
    path = r"C:\Users"
    template = rt"{path}\n\t"
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert isinstance(template.args[0], str)
    assert template.args[0] == ""
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == r"C:\Users"
    assert isinstance(template.args[2], str)
    assert template.args[2] == r"\n\t"


def test_empty_template_with_whitespace():
    """Test template with only whitespace maintains correct interleaving"""
    template = t"   "
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "   "


@pytest.mark.skipif(
    _BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor not fully implemented"
)
def test_template_constructor_with_only_interpolations():
    """Test Template constructor with only interpolations"""
    x = Interpolation(1, "1")
    y = Interpolation(2, "2")
    template = Template(x, y)
    assert len(template.args) == 5
    assert template.args[0] == ""
    assert template.args[1] is x
    assert template.args[2] == ""
    assert template.args[3] is y
    assert template.args[4] == ""


@pytest.mark.skipif(
    _BUG_TEMPLATE_CONSTRUCTOR, reason="Template constructor not fully implemented"
)
def test_template_constructor_with_only_strings():
    """Test Template constructor with only strings"""
    template = Template("Hello", " ", "World")
    assert len(template.args) == 1
    assert template.args[0] == "Hello World"


@pytest.mark.asyncio
async def test_await_in_interpolation():
    """Test that await is allowed in interpolations"""

    async def get_value():
        await asyncio.sleep(0.01)
        return 42

    template = t"Value: {await get_value()}"
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template eq not implemented")
def test_template_equality_with_different_expr():
    """Test that templates with same values but different expressions are not equal"""
    x = 1
    y = 1
    template1 = t"{x}"
    template2 = t"{y}"
    # Even though values are equal, expressions are different
    assert template1 != template2


def test_template_multiline_string_whitespace():
    """Test whitespace handling in multiline template strings"""
    value = 42
    template = t"""
        First line
        {value}
            Indented line
    """
    assert isinstance(template, Template)
    assert len(template.args) == 3
    assert template.args[0].startswith("\n")
    assert "    Indented line" in template.args[2]


def test_template_with_expressions_up_to_16():
    """Test templates with up to 16 expressions, which is known to work."""

    def build_template(n, extra=""):
        return "t'" + ("{x} " * n) + extra + "'"

    x = "X"
    # Test up to 16 expressions (known working limit)
    for i in range(1, 16):
        template = eval(build_template(i))
        assert isinstance(template, Template)
        assert (
            len(template.args) == 2 * i + 1
        )  # expressions + strings between them + trailing string
        assert all(
            isinstance(template.args[j], str) for j in range(0, len(template.args), 2)
        )
        assert all(
            isinstance(template.args[j], Interpolation)
            for j in range(1, len(template.args), 2)
        )


@pytest.mark.skipif(
    _BUG_MANY_EXPRESSIONS, reason="Templates with many expressions not supported"
)
def test_template_with_many_expressions_direct():
    working = t"{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}{29}{30}"
    assert isinstance(working, Template)
    # This next line currently raises a TypeError exception:
    # TypeError: sequence item 0: expected str instance, templatelib.Interpolation found
    busted = t"{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}{29}{30}{31}"
    assert isinstance(busted, Template)


@pytest.mark.skipif(
    _BUG_MANY_EXPRESSIONS, reason="Templates with many expressions not supported"
)
def test_template_with_many_expressions():
    """Test templates with more than 16 expressions.
    Current implementation raises MemoryError for more than 16 expressions."""

    def build_template(n, extra=""):
        return "t'" + ("{x} " * n) + extra + "'"

    x = "X"
    # Test well beyond 16 expressions
    for i in range(250, 260):
        template = eval(build_template(i))
        assert isinstance(template, Template)
        assert (
            len(template.args) == 2 * i + 1
        )  # expressions + strings between them + trailing string
        assert all(
            isinstance(template.args[j], str) for j in range(0, len(template.args), 2)
        )
        assert all(
            isinstance(template.args[j], Interpolation)
            for j in range(1, len(template.args), 2)
        )
