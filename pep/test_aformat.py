import asyncio

import pytest

from . import Template, t
from .aformat import aformat
from .fstring import f

#
# The following tests are specific to the aformat() function. They test the
# async behavior of the function, and the ability to use callable and awaitable
# values in the template.
#


@pytest.mark.asyncio
async def test_async_value():
    async def value():
        return 42

    template: Template = t"{value:.2f}"
    assert await aformat(template) == "42.00"


@pytest.mark.asyncio
async def test_multiple_async_values():
    async def value1():
        await asyncio.sleep(0.1)
        return 42

    async def value2():
        await asyncio.sleep(0.2)
        return 99

    template: Template = t"{value1:.2f} {value2:.2f}"
    assert await aformat(template) == "42.00 99.00"


@pytest.mark.asyncio
async def test_callable_value():
    def value():
        return 42

    template: Template = t"{value:.2f}"
    assert await aformat(template) == "42.00"


# XXX this test does not yet work given the current implementation
# of PEP750 in cpython and the implementation of t() on top of it.
# This will change when Lysandros Nikolaou's implementation of PEP750
# is updated to match the current spec.
# @pytest.mark.asyncio
# async def test_await_in_interpolation():
#     async def value():
#         await asyncio.sleep(0.1)
#         return 42

#     template: Template = t"{await value():.2f}"
#     assert f(template) == "42.00"


#
# The tests below exactly mimimc those in `test_fstring.py`, but using the
# aformat() method. They're probably not super interesting; I included them
# just to make sure that the aformat() function behaves the same as the f()
# function in normal cases. -Dave
#


@pytest.mark.asyncio
async def test_empty():
    template: Template = t""
    assert await aformat(template) == f""


@pytest.mark.asyncio
async def test_simple():
    template: Template = t"hello"
    assert await aformat(template) == f"hello"


@pytest.mark.asyncio
async def test_only_interpolation():
    template: Template = t"{42}"
    assert await aformat(template) == f"{42}"


@pytest.mark.asyncio
async def test_mixed():
    v = 99
    template: Template = t"hello{42}world{v}goodbye"
    assert await aformat(template) == f"hello{42}world{v}goodbye"


@pytest.mark.asyncio
async def test_conv_a():
    template: Template = t"{'🎉'!a}"
    assert await aformat(template) == f"{'🎉'!a}"


@pytest.mark.asyncio
async def test_conv_r():
    template: Template = t"{42!r}"
    assert await aformat(template) == f"{42!r}"


@pytest.mark.asyncio
async def test_conv_s():
    template: Template = t"{42!s}"
    assert await aformat(template) == f"{42!s}"


@pytest.mark.asyncio
async def test_format_spec():
    template: Template = t"{42:04d}"
    assert await aformat(template) == f"{42:04d}"


@pytest.mark.asyncio
async def test_format_spec_and_conv():
    template: Template = t"{42!r:>8}"
    assert await aformat(template) == f"{42!r:>8}"


@pytest.mark.asyncio
async def test_pep_example():
    name = "World"
    value = 42.0
    template: Template = t"Hello {name!r}, value: {value:.2f}"
    assert await aformat(template) == "Hello 'World', value: 42.00"
