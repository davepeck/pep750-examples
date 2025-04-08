"""
Demonstrate structured logging with t-strings and Python's
standard logging module.

See the structured logging example section in PEP 750 for more
information.
"""

from json import JSONEncoder
from logging import Formatter, LogRecord
from typing import Any, Literal, Mapping, Protocol

from string.templatelib import Interpolation, Template

from .fstring import f


class Encoder(Protocol):
    def encode(self, o: Any) -> str: ...


# -----------------------------------------------------------------------------
# Structured logging approach 1: Define a custom message type
# -----------------------------------------------------------------------------


class TemplateMessage:
    def __init__(self, template: Template, encoder: Encoder | None = None) -> None:
        self.template = template
        self.encoder = encoder or JSONEncoder()

    @property
    def message(self) -> str:
        return f(self.template)

    @property
    def values(self) -> Mapping[str, object]:
        return {
            item.expression: item.value
            for item in self.template
            if isinstance(item, Interpolation)
        }

    @property
    def data(self) -> Mapping[str, object]:
        return {"message": self.message, "values": self.values}

    def __str__(self) -> str:
        return self.encoder.encode(self.data)


def make_template_message(encoder: Encoder | None = None):
    """Utility function to create a new message class with a consistent encoder."""

    def _make(template: Template) -> TemplateMessage:
        return TemplateMessage(template, encoder)

    return _make


# -----------------------------------------------------------------------------
# Structured logging approach 2: define custom formatters
# -----------------------------------------------------------------------------


# This type is not publicly available from the `logging` module.
type FormatStyle = Literal["%", "{", "$"]


class TemplateFormatterBase(Formatter):
    """Base class for formatters that use Templates for structured logging."""

    encoder: Encoder

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: FormatStyle = "%",
        validate: bool = True,
        *,
        defaults: Mapping[str, Any] | None = None,
        encoder: Encoder | None = None,
    ):
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.encoder = encoder or JSONEncoder()


class MessageFormatter(TemplateFormatterBase):
    """A formatter that formats a human-readable message from a Template."""

    def message(self, template: Template) -> str:
        return f(template)

    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.message(msg)


class ValuesFormatter(TemplateFormatterBase):
    """A formatter that formats structured output from a Template's values."""

    def values(self, template: Template) -> Mapping[str, object]:
        return {
            item.expression: item.value
            for item in template
            if isinstance(item, Interpolation)
        }

    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.encoder.encode(self.values(msg))


class CombinedFormatter(MessageFormatter, ValuesFormatter):
    """A formatter that formats both a human-readable message and structured output."""

    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.encoder.encode(
            {"message": self.message(msg), "values": self.values(msg)}
        )
