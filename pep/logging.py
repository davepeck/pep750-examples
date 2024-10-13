"""
Demonstrate structured logging with t-strings and Python's
standard logging module.
"""

from json import JSONEncoder
from logging import Formatter, LogRecord
from typing import Any, Protocol

from . import Interpolation, Template, t
from .fstring import f


class Encoder(Protocol):
    def encode(self, o: Any) -> str: ...


class TemplateMessageMaker:
    def __init__(self, encoder: Encoder | None = None) -> None:
        self.encoder = encoder or JSONEncoder()

    def __call__(self, template: Template) -> "TemplateMessage":
        return TemplateMessage(template, encoder=self.encoder)


class TemplateMessage:
    def __init__(self, template: Template, encoder: Encoder | None = None) -> None:
        self._template = template
        self.encoder = encoder or JSONEncoder()

    @property
    def message(self) -> str:
        return f(self._template)

    @property
    def values(self) -> dict[str, Any]:
        return {
            arg.expr: arg.value
            for arg in self._template.args
            if isinstance(arg, Interpolation)
        }

    @property
    def data(self) -> dict[str, Any]:
        return {"message": self.message, "values": self.values}

    def __str__(self) -> str:
        return self.encoder.encode(self.data)


class HumanFormatter(Formatter):
    def format(self, record: Any) -> str:
        msg = record.msg
        if not isinstance(msg, TemplateMessage):
            return super().format(record)
        return msg.message


class StructuredFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        msg = record.msg
        if not isinstance(msg, TemplateMessage):
            return super().format(record)
        return str(msg.encoder.encode(msg.data))
