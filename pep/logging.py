"""
Demonstrate structured logging with t-strings and Python's
standard logging module.
"""

from typing import Any
from json import JSONEncoder

from . import Template, Interpolation, t
from .fstring import f


class TemplateMessage:
    def __init__(
        self, template: Template, encoder: type[JSONEncoder] = JSONEncoder
    ) -> None:
        self._template = template
        self._encoder = encoder

    def data(self) -> dict[str, Any]:
        message = f(self._template)
        values = {
            arg.expr: arg.value
            for arg in self._template.args
            if isinstance(arg, Interpolation)
        }
        return {"message": message, "values": values}

    def __str__(self) -> str:
        return self._encoder().encode(self.data())

