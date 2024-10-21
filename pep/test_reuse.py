from . import Template, t
from .reuse import Formatter


def test_formatter():
    template: Template = t"This is a {'thing'} with value {'value':.2f}"
    formatter = Formatter(template)
    assert formatter.format(thing="pi", value=3.14159) == "This is a pi with value 3.14"
    assert formatter.format(thing="e", value=2.71828) == "This is a e with value 2.72"
