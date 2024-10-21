"""
An example of how to build 'reusable' templates given the facilities
provided by PEP 750.

The question on the table is: how do we get to close to old-style `str.format`
behavior, where we can build up a template and then apply it to multiple
values?
"""

from . import Interpolation, Template
from .fstring import convert


class Formatter:
    def __init__(self, template: Template):
        for arg in template.args:
            if isinstance(arg, Interpolation):
                if not isinstance(arg.value, str):
                    raise ValueError(f"Non-string interpolation: {arg.value}")
        self.template = template

    def format(self, **kwargs) -> str:
        parts = []
        for t_arg in self.template.args:
            if isinstance(t_arg, str):
                parts.append(t_arg)
            else:
                assert isinstance(t_arg.value, str)
                value = kwargs[t_arg.value]
                value = convert(value, t_arg.conv)
                value = format(value, t_arg.format_spec)
                parts.append(value)
        return "".join(parts)
