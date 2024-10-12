from . import t, Template
from .logging import TemplateMessage
from json import JSONEncoder
from decimal import Decimal


def test_template_message_data():
    name = "world"
    template: Template = t"Hello, {name}!"
    message = TemplateMessage(template)
    assert message.data() == {
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
    message = TemplateMessage(template, encoder=DecimalEncoder)
    assert str(message) == '{"message": "$42.10", "values": {"amount": "42.1"}}'
