import pytest
from templatelib import Interpolation, Template

from .format import _parse_fmt_string, from_format

#
# Test the _parse_fmt_string(...) helper function
#


def test_parse_fmt_string_empty():
    assert _parse_fmt_string("") == ()


def test_parse_fmt_string_simple():
    assert _parse_fmt_string("Hello!") == ("Hello!",)


def test_parse_fmt_string_simple_key_interpolation():
    assert _parse_fmt_string("{name}") == ((None, "name", "", None),)


def test_parse_fmt_string_complex_key_interpolation():
    assert _parse_fmt_string("{name!s:.2f}") == ((None, "name", ".2f", "s"),)


def test_parse_fmt_string_simple_auto_index_interpolation():
    assert _parse_fmt_string("{}") == ((0, None, "", None),)


def test_parse_fmt_string_complex_auto_index_interpolation():
    assert _parse_fmt_string("{!s:.2f}") == ((0, None, ".2f", "s"),)


def test_parse_fmt_string_simple_manual_index_interpolation():
    assert _parse_fmt_string("{1}") == ((1, None, "", None),)


def test_parse_fmt_string_complex_manual_index_interpolation():
    assert _parse_fmt_string("{1!s:.2f}") == ((1, None, ".2f", "s"),)


def test_parse_fmt_string_multiple_auto_index_interpolations():
    assert _parse_fmt_string("{}{}") == (
        (0, None, "", None),
        (1, None, "", None),
    )


def test_parse_fmt_string_multiple_manual_index_interpolations():
    assert _parse_fmt_string("{1}{0}") == (
        (1, None, "", None),
        (0, None, "", None),
    )


def test_parse_fmt_string_interleaved_static_and_auto_index():
    assert _parse_fmt_string("Hello, {}! What {}?") == (
        "Hello, ",
        (0, None, "", None),
        "! What ",
        (1, None, "", None),
        "?",
    )


def test_parse_fmt_string_interleaved_static_and_manual_index():
    assert _parse_fmt_string("Hello, {2}! What {17}?") == (
        "Hello, ",
        (2, None, "", None),
        "! What ",
        (17, None, "", None),
        "?",
    )


def test_parse_fmt_string_invalid_auto_to_manual_index():
    with pytest.raises(ValueError):
        _ = _parse_fmt_string("{}{1}")


def test_parse_fmt_string_invalid_manual_to_auto_index():
    with pytest.raises(ValueError):
        _ = _parse_fmt_string("{1}{}")


def test_parse_fmt_string_invalid_conversion_spec():
    with pytest.raises(ValueError):
        _ = _parse_fmt_string("{name!z}")


def test_parse_fmt_string_invalid_conversion_spec_too_many_chars():
    with pytest.raises(ValueError):
        result = _parse_fmt_string("{name!ss}")
        print(result)


def test_fmt_string_mixed_static_auto_and_key_interpolations():
    assert _parse_fmt_string("Hello, {}{name}!") == (
        "Hello, ",
        (0, None, "", None),
        (None, "name", "", None),
        "!",
    )


def test_fmt_string_mixed_static_manual_and_key_interpolations():
    assert _parse_fmt_string("Hello, {1}{name}!") == (
        "Hello, ",
        (1, None, "", None),
        (None, "name", "", None),
        "!",
    )


def test_parse_fmt_string_complex():
    assert _parse_fmt_string("{}{wow}Hello, {}{name!s:.2f}!{:fun}") == (
        (0, None, "", None),
        (None, "wow", "", None),
        "Hello, ",
        (1, None, "", None),
        (None, "name", ".2f", "s"),
        "!",
        (2, None, "fun", None),
    )


def test_parse_fmt_string_nested_interpolations():
    with pytest.raises(NotImplementedError):
        parsed = _parse_fmt_string("{name:{fmt}}")
        print(parsed)


#
# Test the fancy from_format(...) function
#


def _interpolation_almost_eq(i1: Interpolation, i2: Interpolation) -> bool:
    """
    Return True if the two interpolations are almost equal.

    Two interpolations are considered "almost" equal if they have the same
    value, conversion, and format_spec fields. The expr field is not used
    in the comparison.
    """
    return (i1.value, i1.conv, i1.format_spec) == (i2.value, i2.conv, i2.format_spec)


def _almost_eq(t1: Template, t2: Template) -> bool:
    """
    Return True if the two templates are almost equal.

    The one exception allowed is the `expr` field of the Interpolation,
    which is not used in the comparison. That's because there is no canonical
    'correct' expression in cases where the format string uses auto/manual
    indexing, *or* uses something that would normally be taken by t-strings
    and f-strings to be an expression, like "{0 + 1}" -- that's just a key
    for str.format() to use.)
    """
    if len(t1.args) != len(t2.args):
        return False

    for a1, a2 in zip(t1.args, t2.args):
        if isinstance(a1, str):
            if not isinstance(a2, str):
                return False
            if a1 != a2:
                return False
        else:
            assert isinstance(a1, Interpolation)
            if not isinstance(a2, Interpolation):
                return False

            if not _interpolation_almost_eq(a1, a2):
                return False
    return True


def test_from_format_empty():
    made: Template = from_format("")
    expected: Template = t""
    assert _almost_eq(made, expected)


def test_from_format_simple():
    made: Template = from_format("Hello!")
    expected: Template = t"Hello!"
    assert _almost_eq(made, expected)


def test_from_format_simple_key_interpolation():
    name = "world"
    made: Template = from_format("Hello, {name}!", **locals())
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_complex_key_interpolation():
    name = "world"
    made: Template = from_format("Hello, {name!s:.2f}!", **locals())
    expected: Template = t"Hello, {name!s:.2f}!"
    assert _almost_eq(made, expected)


def test_from_format_simple_auto_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {}!", name)
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_complex_auto_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {!s:.2f}!", name)
    expected: Template = t"Hello, {name!s:.2f}!"
    assert _almost_eq(made, expected)


def test_from_format_simple_manual_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {1}!", 99, name)
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_complex_manual_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {1!s:.2f}!", 99, name)
    expected: Template = t"Hello, {name!s:.2f}!"
    assert _almost_eq(made, expected)


def test_from_format_multiple_auto_index_interpolations():
    made: Template = from_format("{}{}", 99, "world")
    expected: Template = t"{99}{'world'}"
    assert _almost_eq(made, expected)


def test_from_format_multiple_manual_index_interpolations():
    made: Template = from_format("{1}{0}", 99, "world")
    expected: Template = t"{'world'}{99}"
    assert _almost_eq(made, expected)


def test_from_format_interleaved_static_and_auto_index():
    made: Template = from_format("Hello, {}! What {}?", 99, "world")
    expected: Template = t"Hello, {99}! What {'world'}?"
    assert _almost_eq(made, expected)


def test_from_format_interleaved_static_and_manual_index():
    made: Template = from_format("Hello, {2}! What {1}?", 99, "world", 42)
    expected: Template = t"Hello, {42}! What {'world'}?"
    assert _almost_eq(made, expected)


def test_from_format_invalid_auto_to_manual_index():
    with pytest.raises(ValueError):
        _ = from_format("{}{1}", 99, "world")


def test_from_format_invalid_manual_to_auto_index():
    with pytest.raises(ValueError):
        _ = from_format("{1}{}", 99, "world")


def test_from_format_invalid_conversion_spec():
    with pytest.raises(ValueError):
        _ = from_format("{name!z}", name="world")


def test_from_format_invalid_conversion_spec_too_many_chars():
    with pytest.raises(ValueError):
        _ = from_format("{name!ss}", name="world")


def test_from_format_mixed_static_auto_and_key_interpolations():
    name = "world"
    made: Template = from_format("Hello, {}{name}!", 99, name=name)
    expected: Template = t"Hello, {99}{name}!"
    assert _almost_eq(made, expected)


def test_from_format_mixed_static_manual_and_key_interpolations():
    name = "world"
    made: Template = from_format("Hello, {1}{name}!", 42, 99, name=name)
    expected: Template = t"Hello, {99}{name}!"
    assert _almost_eq(made, expected)


def test_from_format_complex():
    name = "world"
    wow = "burrito"
    made: Template = from_format(
        "{}{wow}Hello, {}{name!s:.2f}!{:fun}", 99, 42, 76, name=name, wow=wow
    )
    expected: Template = t"{99}{wow}Hello, {42}{name!s:.2f}!{76:fun}"
    assert _almost_eq(made, expected)


def test_from_format_nested_interpolations():
    with pytest.raises(NotImplementedError):
        _ = from_format("{name:{fmt}}", name="world", fmt=".2f")
