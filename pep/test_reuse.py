from . import Template, t
from .reuse import Formatter


def test_formatter():
    template: Template = t"This is a {'thing'} with value {'value':.2f}"
    formatter = Formatter(template)
    assert formatter.format(thing="pi", value=3.14159) == "This is a pi with value 3.14"
    assert (
        formatter.format(thing="cookie", value=42)
        == "This is a cookie with value 42.00"
    )
