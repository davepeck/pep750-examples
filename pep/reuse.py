"""
An example of how to build 'reusable' templates given the facilities
provided by PEP 750.

The question on the table is: how do we get to close to old-style `str.format`
behavior, where we can build up a template and then apply it to multiple
values?
"""

from string.templatelib import Interpolation, Template

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
        for item in template:
            if isinstance(item, Interpolation):
                if not isinstance(item.value, str):
                    raise ValueError(f"Non-string interpolation: {item.value}")
        self.template = template

    def format(self, **kwargs) -> str:
        """Render the t-string using the given values."""
        parts = []
        for item in self.template:
            if isinstance(item, str):
                parts.append(item)
            else:
                assert isinstance(item.value, str)
                value = kwargs[item.value]
                value = convert(value, item.conversion)
                value = format(value, item.format_spec)
                parts.append(value)
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
        for item in template:
            if isinstance(item, Interpolation):
                if not isinstance(item.value, str):
                    raise ValueError(f"Non-string interpolation: {item.value}")
        self.template = template

    def bind(self, **kwargs) -> Template:
        """Bind values to the template."""
        items = []
        for item in self.template:
            if isinstance(item, str):
                items.append(item)
            else:
                assert isinstance(item.value, str)
                value = kwargs[item.value]
                expr = repr(item.value)[1:-1]  # remove quotes from original expression
                interpolation = Interpolation(
                    value, expr, item.conversion, item.format_spec
                )
                items.append(interpolation)
        return Template(*items)
