import pytest
from string.templatelib import Template

from .reuse import Binder, Formatter


def test_formatter():
    template: Template = t"The {'cheese'} costs ${'amount':,.2f}"
    formatter = Formatter(template)
    formatted = formatter.format(cheese="Roquefort", amount=15.7)
    assert formatted == "The Roquefort costs $15.70"


def test_binder():
    template: Template = t"The {'cheese'} costs ${'amount':,.2f}"
    binder = Binder(template)
    bound = binder.bind(cheese="Roquefort", amount=15.7)
    cheese = "Roquefort"
    amount = 15.7
    # assert bound == t"The {cheese} costs ${amount:,.2f}"
    assert bound.strings == ("The ", " costs $", "")
    assert bound.interpolations[0].value == cheese
    assert bound.interpolations[1].value == amount
