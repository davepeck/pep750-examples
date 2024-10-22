from . import Template, t
from .lazy import format_some


def test_format_some():
    template: Template = t"{'roquefort':blue} {'limburger':stinky}"
    assert format_some("blue", template) == "roquefort ***"
    assert format_some("stinky", template) == "*** limburger"


def test_format_some_lambdas():
    # Just imagine that our lambdas are expensive to compute; later, we'll
    # decide which ones we actually need.
    template: Template = t"{(lambda: 'roquefort'):blue} {(lambda: 'limburger'):stinky}"
    assert format_some("blue", template) == "roquefort ***"
    assert format_some("stinky", template) == "*** limburger"
