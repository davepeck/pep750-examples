"""
An example of how to build 'reusable' templates given the facilities
provided by PEP 750.

The question on the table is: how do we get to close to old-style `str.format`
behavior, where we can build up a template and then apply it to multiple
values?
"""

from templatelib import Interpolation, Template

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
        for arg in template.args:
            if isinstance(arg, Interpolation):
                if not isinstance(arg.value, str):
                    raise ValueError(f"Non-string interpolation: {arg.value}")
        self.template = template

    def format(self, **kwargs) -> str:
        """Render the t-string using the given values."""
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


class Binder:
    """
    Class to bind values to a t-string at a later date.

    The t-string must use only strings as interpolation values. These strings
    become the keys in the `kwargs` passed to `bind`.
    """

    def __init__(self, template: Template):
        """Construct a binder for the provided template."""
        # Ensure that all interpolations are strings.
        for arg in template.args:
            if isinstance(arg, Interpolation):
                if not isinstance(arg.value, str):
                    raise ValueError(f"Non-string interpolation: {arg.value}")
        self.template = template

    def bind(self, **kwargs) -> Template:
        """Bind values to the template."""
        args = []
        for t_arg in self.template.args:
            if isinstance(t_arg, str):
                args.append(t_arg)
            else:
                assert isinstance(t_arg.value, str)
                value = kwargs[t_arg.value]
                expr = repr(t_arg.value)[1:-1]  # remove quotes from original expression
                interpolation = Interpolation(
                    value, expr, t_arg.conv, t_arg.format_spec
                )
                args.append(interpolation)
        return Template(*args)
