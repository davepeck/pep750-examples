"""
Implement 'asynchronous' f-string like behavior on top of t-strings.

See also `test_afstring.py`
"""

import inspect

from string.templatelib import Interpolation, Template

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
    for item in template:
        match item:
            case str() as s:
                parts.append(s)
            case Interpolation(value, _, conv, format_spec):
                if inspect.iscoroutinefunction(value):
                    value = await value()
                elif callable(value):
                    value = value()
                value = convert(value, conv)
                value = format(value, format_spec)
                parts.append(value)
    return "".join(parts)
