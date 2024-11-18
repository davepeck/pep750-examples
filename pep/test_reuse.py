import pytest
from templatelib import Template

from . import _MISSING_TEMPLATE_EQ
from .reuse import Binder, Formatter


def test_formatter():
    template: Template = t"The {'cheese'} costs ${'amount':,.2f}"
    formatter = Formatter(template)
    formatted = formatter.format(cheese="Roquefort", amount=15.7)
    assert formatted == "The Roquefort costs $15.70"


@pytest.mark.skipif(_MISSING_TEMPLATE_EQ, reason="Template equality not available")
def test_binder():
    template: Template = t"The {'cheese'} costs ${'amount':,.2f}"
    binder = Binder(template)
    bound = binder.bind(cheese="Roquefort", amount=15.7)
    cheese = "Roquefort"
    amount = 15.7
    assert bound == t"The {cheese} costs ${amount:,.2f}"
