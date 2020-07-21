import asyncio
import time


COROUTINES = []


class LoopEnd(Exception):
    """Loop end exception."""
    pass


async def sleep(tics: int = 1):
    """Sleep for <<tics>> times."""
    for _ in range(tics):
        await asyncio.sleep(0)


def add_coroutine(coroutine):
    """Add coroutine to coroutines list."""
    COROUTINES.append(coroutine)


def loop_forever(windows_for_refresh: list):
    """Loop until at least one coroutine can work."""
    if len(COROUTINES) == 0:
        raise Exception("No coroutines for start")

    index: int = 0
    while COROUTINES:
        if index >= len(COROUTINES):
            index = 0
        coroutine = COROUTINES[index]
        try:
            coroutine.send(None)
            index += 1
        except StopIteration:
            COROUTINES.remove(coroutine)
        except LoopEnd:
            COROUTINES.clear()
            break
        for canvas in windows_for_refresh:
            canvas.refresh()
        time.sleep(0.01)
