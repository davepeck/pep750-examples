import pytest
from templatelib import Interpolation, Template

from .format import _split_field_name, from_format


def test_split_field_name_simple():
    key, rest = _split_field_name("name")
    assert key == "name"
    assert rest == ""


def test_split_field_name_dot():
    key, rest = _split_field_name("name.attr")
    assert key == "name"
    assert rest == ".attr"


def test_split_field_name_bracket():
    key, rest = _split_field_name("name[0]")
    assert key == "name"
    assert rest == "[0]"


def test_split_field_name_dot_bracket():
    key, rest = _split_field_name("name.attr[0]")
    assert key == "name"
    assert rest == ".attr[0]"


def test_split_field_name_bracket_dot():
    key, rest = _split_field_name("name[0].attr")
    assert key == "name"
    assert rest == "[0].attr"


def test_split_field_name_bracket_bracket():
    key, rest = _split_field_name("name[0][1]")
    assert key == "name"
    assert rest == "[0][1]"


def test_split_field_name_empty_key_dot():
    key, rest = _split_field_name(".attr")
    assert key == ""
    assert rest == ".attr"


def test_split_field_name_empty_key_bracket():
    key, rest = _split_field_name("[0]")
    assert key == ""
    assert rest == "[0]"


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


def test_from_format_key_array_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {a[1]}!", a=[99, name])
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_auto_array_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {[1]}!", [99, name])
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_manual_array_index_interpolation():
    name = "world"
    made: Template = from_format("Hello, {0[1]}!", [99, name])
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_key_dot_interpolation():
    name = "world"
    made: Template = from_format("Hello, {a.b}!", a=type("Namespace", (), {"b": name}))
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_auto_dot_interpolation():
    name = "world"
    made: Template = from_format("Hello, {.b}!", type("Namespace", (), {"b": name}))
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_manual_dot_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {1.b}!", "nope", type("Namespace", (), {"b": name})
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_key_dot_array_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {a.b[1]}!", a=type("Namespace", (), {"b": [99, name]})
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_auto_dot_array_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {.b[1]}!", type("Namespace", (), {"b": [99, name]})
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_manual_dot_array_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {1.b[1]}!", "nope", type("Namespace", (), {"b": [99, name]})
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_key_array_dot_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {a[1].b}!", a=[99, type("Namespace", (), {"b": name})]
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_auto_array_dot_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {[1].b}!", [99, type("Namespace", (), {"b": name})]
    )
    expected: Template = t"Hello, {name}!"
    assert _almost_eq(made, expected)


def test_from_format_manual_array_dot_interpolation():
    name = "world"
    made: Template = from_format(
        "Hello, {0[1].b}!", [99, type("Namespace", (), {"b": name})]
    )
    expected: Template = t"Hello, {name}!"
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


def test_from_format_format_spec_with_full_interpolation():
    number = 42
    fmt = ".2f"
    made: Template = from_format("{number:{fmt}}", number=number, fmt=fmt)
    expected: Template = t"{number:{fmt}}"
    assert _almost_eq(made, expected)


def test_from_format_format_spec_with_part_interpolation():
    number = 42
    precision = 2
    made: Template = from_format(
        "{number:.{precision}f}", number=number, precision=precision
    )
    expected: Template = t"{number:.{precision}f}"
    assert _almost_eq(made, expected)


def test_from_format_format_spec_with_multiple_interpolations():
    number = 42
    dot = "."
    precision = 2
    kind = "f"
    made: Template = from_format(
        "{number:{dot}{precision}{kind}}",
        number=number,
        dot=dot,
        precision=precision,
        kind=kind,
    )
    expected: Template = t"{number:{dot}{precision}{kind}}"
    assert _almost_eq(made, expected)
