from . import Template, t
from .lazy import format_some


def test_format_some():
    template: Template = t"{(lambda: 'roquefort'):blue} {(lambda: 'limburger'):stinky}"
    assert format_some("blue", template) == "roquefort ***"
    assert format_some("stinky", template) == "*** limburger"
