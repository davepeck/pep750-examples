"""
Implement 'asynchronous' f-string like behavior on top of t-strings.

See also `test_afstring.py`
"""

import inspect

from templatelib import Template

from . import pairs
from .fstring import convert


async def async_f(template: Template) -> str:
    """
    Implement f-string formatting for async functions.

    This is basically the `f()` function from the `fstring.py` example code,
    but adapted to expect that Interpolation.value may be either a callable
    *or* an awaitable. If it is, we call it and await the result before
    formatting it.
    """
    parts = []
    for i, s in pairs(template):
        if i is not None:
            if inspect.iscoroutinefunction(i.value):
                value = await i.value()
            elif callable(i.value):
                value = i.value()
            value = convert(value, i.conv)
            value = format(value, i.format_spec)
            parts.append(value)
        parts.append(s)
    return "".join(parts)
