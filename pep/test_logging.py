from decimal import Decimal
from json import JSONEncoder

from . import Template, t
from .logging import TemplateMessage, TemplateMessageMaker


def test_template_message_message():
    name = "world"
    template: Template = t"Hello, {name}!"
    message = TemplateMessage(template)
    assert message.message == f"Hello, {name}!"


def test_template_message_values():
    name = "world"
    template: Template = t"Hello, {name}!"
    message = TemplateMessage(template)
    assert message.values == {"name": "world"}


def test_template_message_data():
    name = "world"
    template: Template = t"Hello, {name}!"
    message = TemplateMessage(template)
    assert message.data == {
        "message": f"Hello, {name}!",
        "values": {"name": "world"},
    }


def test_template_message_str():
    name = "world"
    template: Template = t"Hello, {name}!"
    message = TemplateMessage(template)
    assert str(message) == '{"message": "Hello, world!", "values": {"name": "world"}}'


class DecimalEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super().default(o)


def test_template_message_encoder():
    amount = Decimal("42.1")
    template: Template = t"${amount:0.2f}"
    message = TemplateMessage(template, DecimalEncoder())
    assert str(message) == '{"message": "$42.10", "values": {"amount": "42.1"}}'


def test_template_message_maker():
    amount = Decimal("42.1")
    maker = TemplateMessageMaker(DecimalEncoder())
    template: Template = t"${amount:0.2f}"
    message = maker(template)
    assert str(message) == '{"message": "$42.10", "values": {"amount": "42.1"}}'
