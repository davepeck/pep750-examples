import asyncio

from . import Template
from .fstring import convert


async def aformat(template: Template) -> str:
    """
    Implement f-string formatting for async functions.

    This is basically the `f()` function from the `fstring.py` example code,
    but adapted to expect that Interpolation.value may be either a callable
    *or* an awaitable. If it is, we call it and await the result before
    formatting it.
    """
    parts = []
    for arg in template.args:
        if isinstance(arg, str):
            parts.append(arg)
        else:
            value = arg.value
            if asyncio.iscoroutinefunction(value):
                value = await value()
            elif callable(value):
                value = value()
            value = convert(value, arg.conv)
            value = format(value, arg.format_spec)
            parts.append(value)
    return "".join(parts)
