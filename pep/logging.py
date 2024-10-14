"""
Demonstrate structured logging with t-strings and Python's
standard logging module.
"""

from json import JSONEncoder
from logging import Formatter, LogRecord
from typing import Any, Literal, Mapping, Protocol

from . import Interpolation, Template, t
from .fstring import f


class Encoder(Protocol):
    def encode(self, o: Any) -> str: ...


#
# Approach 1: Define a custom message type
#


class TemplateMessageMaker:
    def __init__(self, encoder: Encoder | None = None) -> None:
        self.encoder = encoder or JSONEncoder()

    def __call__(self, template: Template) -> "TemplateMessage":
        return TemplateMessage(template, encoder=self.encoder)


class TemplateMessage:
    def __init__(self, template: Template, encoder: Encoder | None = None) -> None:
        self.template = template
        self.encoder = encoder or JSONEncoder()

    @property
    def message(self) -> str:
        return f(self.template)

    @property
    def values(self) -> Mapping[str, Any]:
        return {
            arg.expr: arg.value
            for arg in self.template.args
            if isinstance(arg, Interpolation)
        }

    @property
    def data(self) -> Mapping[str, Any]:
        return {"message": self.message, "values": self.values}

    def __str__(self) -> str:
        return self.encoder.encode(self.data)


#
# Approach 2: Define custom formatters
#


type FormatStyle = Literal["%", "{", "$"]


class TemplateFormatterBase(Formatter):
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
    def message(self, template: Template) -> str:
        return f(template)

    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.message(msg)


class ValuesFormatter(TemplateFormatterBase):
    def values(self, template: Template) -> Mapping[str, Any]:
        return {
            arg.expr: arg.value
            for arg in template.args
            if isinstance(arg, Interpolation)
        }

    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.encoder.encode(self.values(msg))


class CombinedFormatter(MessageFormatter, ValuesFormatter):
    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, Template):
            return super().format(record)
        return self.encoder.encode(
            {"message": self.message(msg), "values": self.values(msg)}
        )
