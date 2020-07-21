import curses

import eventloop

from .garbage import OBSTACLES, OBSTACLES_IN_LAST_COLLISIONS
from .curses_tools import getmaxyx_border, Window


async def fire(canvas: Window, start_row: float, start_column: float, rows_speed: float = -0.3,
               columns_speed: int = 0) -> None:
    """Display animation of gun shot, direction and speed can be specified."""
    row: float
    column: float

    rows: int
    columns: int
    max_row: int
    max_column: int

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await eventloop.sleep(1)

    canvas.addstr(round(row), round(column), 'O')
    await eventloop.sleep(1)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol: str = '-' if columns_speed else '|'

    rows, columns = getmaxyx_border(canvas)
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        collision: bool = False
        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column, 1, 1):
                collision = True
                OBSTACLES_IN_LAST_COLLISIONS.append(obstacle)
                break
        if collision:
            break
        canvas.addstr(round(row), round(column), symbol)
        await eventloop.sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed
