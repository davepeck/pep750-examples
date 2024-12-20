"""
An example of how to build 'reusable' templates given the facilities
provided by PEP 750.

The question on the table is: how do we get to close to old-style `str.format`
behavior, where we can build up a template and then apply it to multiple
values?
"""

from templatelib import Interpolation, Template

from . import pairs
from .fstring import convert


class Formatter:
    """
    Class to format a t-string with values.

    The t-string must use only strings as interpolation values. These strings
    become the keys in the `kwargs` passed to `format`.
    """

    def __init__(self, template: Template):
        """Construct a formatter for the provided template."""
        # Ensure that all interpolations are strings.
        for i, _ in pairs(template):
            if i is not None and not isinstance(i.value, str):
                raise ValueError(f"Non-string interpolation: {i.value}")
        self.template = template

    def format(self, **kwargs) -> str:
        """Render the t-string using the given values."""
        parts = []
        for i, s in pairs(self.template):
            if i is not None:
                assert isinstance(i.value, str)
                value = kwargs[i.value]
                value = convert(value, i.conv)
                value = format(value, i.format_spec)
                parts.append(value)
            parts.append(s)
        return "".join(parts)


class Binder:
    """
    Class to bind values to a t-string at a later date.

    The t-string must use only strings as interpolation values. These strings
    become the keys in the `kwargs` passed to `bind`.
    """

    def __init__(self, template: Template):
        """Construct a binder for the provided template."""
        # Ensure that all interpolations are strings.
        for i, _ in pairs(template):
            if i is not None and not isinstance(i.value, str):
                raise ValueError(f"Non-string interpolation: {i.value}")
        self.template = template

    def bind(self, **kwargs) -> Template:
        """Bind values to the template."""
        args = []
        for i, s in pairs(self.template):
            if i is not None:
                assert isinstance(i.value, str)
                value = kwargs[i.value]
                expr = repr(i.value)[1:-1]  # remove quotes from original expression
                interpolation = Interpolation(value, expr, i.conv, i.format_spec)
                args.append(interpolation)
            args.append(s)
        return Template(*args)
