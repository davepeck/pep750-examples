import asyncio

import pytest
from templatelib import Template

from .afstring import async_f
from .fstring import f

#
# The following tests are specific to the async_f() function. They test the
# async behavior of the function, and the ability to use callable and awaitable
# values in the template.
#


@pytest.mark.asyncio
async def test_async_value():
    async def value():
        return 42

    template: Template = t"{value:.2f}"
    assert await async_f(template) == "42.00"


@pytest.mark.asyncio
async def test_multiple_async_values():
    async def value1():
        await asyncio.sleep(0.1)
        return 42

    async def value2():
        await asyncio.sleep(0.2)
        return 99

    template: Template = t"{value1:.2f} {value2:.2f}"
    assert await async_f(template) == "42.00 99.00"


@pytest.mark.asyncio
async def test_callable_value():
    def value():
        return 42

    template: Template = t"{value:.2f}"
    assert await async_f(template) == "42.00"


@pytest.mark.asyncio
async def test_lambda_value():
    template: Template = t"{(lambda: 42):.2f}"
    assert await async_f(template) == "42.00"


@pytest.mark.asyncio
async def test_lambda_unbound():
    template: Template = t"{(lambda: name)}"

    async def reuse(name: str) -> str:
        return await async_f(template)

    with pytest.raises(NameError):
        await reuse("nope")


@pytest.mark.asyncio
async def test_await_in_interpolation():
    async def value():
        await asyncio.sleep(0.1)
        return 42

    template: Template = t"{await value():.2f}"
    assert f(template) == "42.00"
