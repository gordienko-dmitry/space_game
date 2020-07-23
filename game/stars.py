from typing import List, Tuple
import curses
import random

import eventloop

from .curses_tools import getmaxyx_border, Window


BORDER_LENGTH = 2


async def blink_star(canvas: Window, count: int = 150) -> None:
    """Stars blinking loop."""
    height: int
    width: int
    height, width = getmaxyx_border(canvas)
    stars_info: List[Tuple[int, int, str]] = [(random.randint(BORDER_LENGTH, height - BORDER_LENGTH),
                                               random.randint(BORDER_LENGTH, width - BORDER_LENGTH),
                                               random.choice("+*.:")) for _ in range(count)]

    # Prepare stars
    row: int
    column: int
    symbol: str
    for row, column, symbol in stars_info:
        canvas.addstr(row, column, symbol, curses.A_DIM)

    row, column, symbol = stars_info[0]

    # Eternal blinking loop
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await eventloop.sleep(20)

        row, column, symbol = random.choice(stars_info)

        canvas.addstr(row, column, symbol)
        await eventloop.sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await eventloop.sleep(5)

        canvas.addstr(row, column, symbol)
        await eventloop.sleep(3)
