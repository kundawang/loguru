from loguru import logger
import asyncio
import sys

logger.remove()

# We're truly only testing whether the tests succeed, we do not care about the formatting.
# These should be regular Pytest test cases, but that is not possible because the syntax is not valid in Python 3.5.
logger.add(lambda m: None, format="", diagnose=True, backtrace=True, colorize=True)

def test_decorate_async_generator():
    @logger.catch(reraise=True)
    async def generator(x, y):
        yield x
        yield y

    async def coro():
        out = []
        async for val in generator(1, 2):
            out.append(val)
        return out

    res = asyncio.run(coro())
    assert res == [1, 2]


def test_decorate_async_generator_with_error():
    @logger.catch(reraise=False)
    async def generator(x, y):
        yield x
        yield y
        raise ValueError

    async def coro():
        out = []
        async for val in generator(1, 2):
            out.append(val)
        return out

    res = asyncio.run(coro())
    assert res == [1, 2]

def test_decorate_async_generator_with_error_reraised():
    @logger.catch(reraise=True)
    async def generator(x, y):
        yield x
        yield y
        raise ValueError

    async def coro():
        out = []
        try:
            async for val in generator(1, 2):
                out.append(val)
        except ValueError:
            pass
        else:
            raise AssertionError("ValueError not raised")
        return out

    res = asyncio.run(coro())
    assert res == [1, 2]


def test_decorate_async_generator_then_async_send():
    @logger.catch
    async def generator(x, y):
        yield x
        yield y

    async def coro():
        gen = generator(1, 2)
        await gen.asend(None)
        await gen.asend(None)
        try:
            await gen.asend(None)
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("StopAsyncIteration not raised")

    asyncio.run(coro())


def test_decorate_async_generator_then_async_throw():
    @logger.catch
    async def generator(x, y):
        yield x
        yield y

    async def coro():
        gen = generator(1, 2)
        await gen.asend(None)
        try:
            await gen.athrow(ValueError)
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("StopAsyncIteration not raised")

    asyncio.run(coro())


def test_decorate_async_generator_then_async_throw_with_handled_error():
    @logger.catch
    async def generator():
        try:
            yield 1
        except ValueError:
            pass

    async def coro():
        gen = generator()
        await gen.asend(None)
        try:
            await gen.athrow(ValueError)
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("StopAsyncIteration not raised")

    asyncio.run(coro())


def test_decorate_async_generator_then_async_throw_is_logged():
    messages = []
    handler_id = logger.add(
        messages.append, format="{message}", diagnose=False, backtrace=False, colorize=False
    )

    @logger.catch(default=42)
    async def generator():
        yield 1
        yield 2

    async def coro():
        gen = generator()
        await gen.asend(None)
        try:
            await gen.athrow(ValueError("Bug"))
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("StopAsyncIteration not raised")

    try:
        asyncio.run(coro())
    finally:
        logger.remove(handler_id)

    if not any("ValueError: Bug" in str(message) for message in messages):
        raise AssertionError("Exception raised by athrow() was not logged")


def test_decorate_async_generator_then_async_throw_with_new_error_is_logged():
    messages = []
    handler_id = logger.add(
        messages.append, format="{message}", diagnose=False, backtrace=False, colorize=False
    )

    @logger.catch(default=42)
    async def generator():
        try:
            yield 1
        except ValueError:
            raise KeyError("other")

    async def coro():
        gen = generator()
        await gen.asend(None)
        try:
            await gen.athrow(ValueError("Bug"))
        except StopAsyncIteration:
            pass
        else:
            raise AssertionError("StopAsyncIteration not raised")

    try:
        asyncio.run(coro())
    finally:
        logger.remove(handler_id)

    if not any("KeyError: 'other'" in str(message) for message in messages):
        raise AssertionError("Error raised while handling athrow() was not logged")


test_decorate_async_generator()
test_decorate_async_generator_with_error()
test_decorate_async_generator_with_error_reraised()
test_decorate_async_generator_then_async_send()
test_decorate_async_generator_then_async_throw()
test_decorate_async_generator_then_async_throw_with_handled_error()
test_decorate_async_generator_then_async_throw_is_logged()
test_decorate_async_generator_then_async_throw_with_new_error_is_logged()

logger.add(sys.stderr, format="{message}")
logger.info("Done")
