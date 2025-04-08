import io
import logging
from decimal import Decimal
from json import JSONEncoder
from string.templatelib import Template

from .logging import (
    CombinedFormatter,
    MessageFormatter,
    TemplateMessage,
    ValuesFormatter,
    make_template_message,
)

# -----------------------------------------------------------------------------
# Tests for approach 1: Define a custom message type
# -----------------------------------------------------------------------------


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
    maker = make_template_message(DecimalEncoder())
    template: Template = t"${amount:0.2f}"
    message = maker(template)
    assert str(message) == '{"message": "$42.10", "values": {"amount": "42.1"}}'


# -----------------------------------------------------------------------------
# Tests for approach 2: Define custom formatters
# -----------------------------------------------------------------------------


def test_message_formatter():
    logger = logging.getLogger("pep.logging.example")
    logger.setLevel(logging.INFO)

    message_stream = io.StringIO()
    message_handler = logging.StreamHandler(message_stream)
    message_handler.setFormatter(MessageFormatter())
    logger.addHandler(message_handler)

    name = "world"
    logger.info(t"Hello, {name}!")
    assert message_stream.getvalue() == f"Hello, {name}!\n"


def test_values_formatter():
    logger = logging.getLogger("pep.logging.example")
    logger.setLevel(logging.INFO)

    values_stream = io.StringIO()
    values_handler = logging.StreamHandler(values_stream)
    values_handler.setFormatter(ValuesFormatter())
    logger.addHandler(values_handler)

    name = "world"
    logger.info(t"Hello, {name}!")
    assert values_stream.getvalue() == '{"name": "world"}\n'


def test_both_formatters():
    logger = logging.getLogger("pep.logging.example")
    logger.setLevel(logging.INFO)

    message_stream = io.StringIO()
    message_handler = logging.StreamHandler(message_stream)
    message_handler.setFormatter(MessageFormatter())
    logger.addHandler(message_handler)

    values_stream = io.StringIO()
    values_handler = logging.StreamHandler(values_stream)
    values_handler.setFormatter(ValuesFormatter())
    logger.addHandler(values_handler)

    name = "world"
    logger.info(t"Hello, {name}!")
    assert message_stream.getvalue() == f"Hello, {name}!\n"
    assert values_stream.getvalue() == '{"name": "world"}\n'


def test_combined_formatter():
    logger = logging.getLogger("pep.logging.example")
    logger.setLevel(logging.INFO)

    combined_stream = io.StringIO()
    combined_handler = logging.StreamHandler(combined_stream)
    combined_handler.setFormatter(CombinedFormatter())
    logger.addHandler(combined_handler)

    name = "world"
    logger.info(t"Hello, {name}!")
    assert (
        combined_stream.getvalue()
        == '{"message": "Hello, world!", "values": {"name": "world"}}\n'
    )


def test_both_formatters_with_dictconfig():
    import logging.config

    logging.config.dictConfig(
        {
            "version": 1,
            "formatters": {
                "message": {"()": MessageFormatter},
                "values": {"()": ValuesFormatter},
            },
            "handlers": {
                "human": {
                    "class": "logging.StreamHandler",
                    "formatter": "message",
                    "stream": "ext://sys.stdout",
                },
                "structured": {
                    "class": "logging.StreamHandler",
                    "formatter": "values",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "pep.logging.example": {
                    "level": "INFO",
                    "handlers": ["human", "structured"],
                }
            },
        }
    )

    logger = logging.getLogger("pep.logging.example")

    message_stream = io.StringIO()
    values_stream = io.StringIO()

    for handler in logger.handlers:
        assert isinstance(handler, logging.StreamHandler)
        assert isinstance(handler.formatter, (MessageFormatter, ValuesFormatter))
        if isinstance(handler.formatter, MessageFormatter):
            handler.setStream(message_stream)
        else:
            assert isinstance(handler.formatter, ValuesFormatter)
            handler.setStream(values_stream)

    name = "world"
    logger.info(t"Hello, {name}!")

    assert message_stream.getvalue() == f"Hello, {name}!\n"
    assert values_stream.getvalue() == '{"name": "world"}\n'
