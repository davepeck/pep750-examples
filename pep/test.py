"""
Test that our implementation of PEP 750, which is currently partially in the
fork of cpython, and partially in the __init__.py in this repository, works.

See the __init__.py for a more detailed explanation.
"""

from . import Interpolation, Template, _interleave, t


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


def test_format_spec_and_conv():
    template = t"{42!r:04d}"
    assert isinstance(template, Template)
    assert isinstance(template.args[1], Interpolation)
    assert template.args[1].value == 42
    assert template.args[1].conv == "r"
    assert template.args[1].format_spec == "04d"


def test_add_template_str():
    template = t"hello" + "world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


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


def test_add_template_template():
    template = t"hello" + t"world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


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


def test_add_str_template():
    template = "hello" + t"world"
    assert isinstance(template, Template)
    assert len(template.args) == 1
    assert isinstance(template.args[0], str)
    assert template.args[0] == "hello" + "world"


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


# This is not supported with the current branch of cpython
# def test_implicit_concat_str_template():
#     template = "hello" t"world"
#     assert isinstance(template, Template)
#     assert len(template.args) == 1
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello" + "world"

# Nor is this
# def test_implicit_concat_template_str():
#     template = t"hello" "world"
#     assert isinstance(template, Template)
#     assert len(template.args) == 1
#     assert isinstance(template.args[0], str)
#     assert template.args[0] == "hello" + "world"


def test_template_eq_1():
    assert t"hello" == t"hello"


def test_template_eq_2():
    assert t"hello" != t"world"


def test_template_eq_3():
    planet = "earth"
    assert t"hello {planet}" == t"hello {planet}"


def test_template_eq_4():
    planet = "earth"
    satellite = "moon"
    assert t"hello {planet}" != t"hello {satellite}"


def test_template_eq_5():
    assert "hello" + t" {42}" == t"hello {42}"


def test_template_eq_6():
    assert t"hello {42}" + "!" == t"hello {42}!"


def test_template_eq_7():
    assert t"{42}" + t"{99}" == t"{42}{99}"


def test_interleave_empty():
    assert _interleave() == ("",)


def test_interleave_simple():
    assert _interleave("hello") == ("hello",)


def test_interleave_interpolation():
    i1 = Interpolation(42, "i1", None, "")
    assert _interleave(i1) == ("", i1, "")


def test_interleave_neighboring_interpolations():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    assert _interleave(i1, i2) == ("", i1, "", i2, "")


def test_interleave_neighboring_strings():
    assert _interleave("hello", "world") == ("helloworld",)


def test_interleave_all_the_things():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    i3 = Interpolation(100, "i3", None, "")
    i4 = Interpolation(101, "i4", None, "")
    assert _interleave("hello", "there", i1, i2, "wow", "neat", i3, i4) == (
        "hellothere",
        i1,
        "",
        i2,
        "wowneat",
        i3,
        "",
        i4,
        "",
    )
