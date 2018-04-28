import asyncio


def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(func(*args, **kwargs))
    loop.run_until_complete(future)
    return future.result()
