"""
Test our 'implementation' of f-string behavior as seen in PEP 750.
"""


from . import t, Template
from .fstring import f


def test_empty():
    template: Template = t""
    assert f(template) == f""

def test_simple():
    template: Template = t"hello"
    assert f(template) == f"hello"

def test_only_interpolation():
    template: Template = t"{42}"
    assert f(template) == f"{42}"

def test_mixed():
    v = 99
    template: Template = t"hello{42}world{v}goodbye"
    assert f(template) == f"hello{42}world{v}goodbye"

def test_conv_a():
    template: Template = t"{'🎉'!a}"
    assert f(template) == f"{'🎉'!a}"

def test_conv_r():
    template: Template = t"{42!r}"
    assert f(template) == f"{42!r}"

def test_conv_s():
    template: Template = t"{42!s}"
    assert f(template) == f"{42!s}"

def test_format_spec():
    template: Template = t"{42:04d}"
    assert f(template) == f"{42:04d}"

def test_format_spec_and_conv():
    template: Template = t"{42!s:>8}"
    assert f(template) == f"{42!r:>8}"

def test_pep_example():
    name = "World"
    value = 42.0
    template: Template = t"Hello {name!r}, value: {value:.2f}"
    assert f(template) == "Hello 'World', value: 42.00"

def test_raises_the_same_exception():
    invalid_template: Template = t"{42!s:04d}"
    try:
        f(invalid_template)
    except ValueError as e:
        expected_message = str(e)
    else:
        assert False, "Expected ValueError"

    try:
        _ = f"{42!s:04d}"
    except ValueError as e:
        assert str(e) == expected_message
    else:
        assert False, "Expected ValueError"
