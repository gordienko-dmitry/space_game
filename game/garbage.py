from typing import Union
import random
import curses

import eventloop

from .curses_tools import draw_frame, getmaxyx_border, get_frame_size, Window
from .game_scenario import get_garbage_delay_tics
from .frames import read_frames_from_folder
from .settings import GARBAGE_PATH
from .obstacles import Obstacle
from .explosion import explode


GARBAGE_FRAMES: list = [frame for frame in read_frames_from_folder(GARBAGE_PATH)]
OBSTACLES_IN_LAST_COLLISIONS: list = []
OBSTACLES: list = []


def clean_field(canvas: Window) -> None:
    """Destroy all garbage objects & clean their view. """
    OBSTACLES_IN_LAST_COLLISIONS.clear()
    for obstacle in OBSTACLES:
        draw_frame(canvas, obstacle.row, obstacle.column, obstacle.frame, negative=True)
    OBSTACLES.clear()


async def fill_orbit_with_garbage(canvas: Window) -> None:
    """Add garbage to window every tics count."""
    width: int
    frame_height: int
    frame_width: int

    _, width = getmaxyx_border(canvas)
    while True:
        tics: Union[int, None] = get_garbage_delay_tics()
        if tics is None:
            await eventloop.sleep(1)
            continue
        await eventloop.sleep(tics)
        frame: str = random.choice(GARBAGE_FRAMES)
        show: bool = True
        column: int = 0
        for _ in range(10):
            column = random.randint(1, width)
            frame_height, frame_width = get_frame_size(frame)
            for obstacle in OBSTACLES:
                if obstacle.has_collision(1, column, frame_height, frame_width):
                    show = False
                    break
            if show:
                break
        if show:
            eventloop.add_coroutine(fly_garbage(canvas, column, frame))


async def fly_garbage(canvas: Window, column: int, garbage_frame: str, speed: float = 0.5):
    """Animate garbage, flying from top to bottom. Column position will stay same, as specified on start."""
    rows_number: int
    columns_number: int
    height: int
    width: int

    rows_number, columns_number = getmaxyx_border(canvas)

    column = max(column, 1)
    column = min(column, columns_number - 1)

    row: float = 1.0

    height, width = get_frame_size(garbage_frame)
    obstacle: Obstacle = Obstacle(round(row), column, garbage_frame, height, width)

    OBSTACLES.append(obstacle)

    while row < rows_number:
        if obstacle not in OBSTACLES:
            break
        if obstacle in OBSTACLES_IN_LAST_COLLISIONS:
            OBSTACLES_IN_LAST_COLLISIONS.remove(obstacle)
            OBSTACLES.remove(obstacle)
            await explode(canvas, round(row + height / 2), round(column + width / 2))
            break
        draw_frame(canvas, round(row), column, garbage_frame)
        await eventloop.sleep(1)
        draw_frame(canvas, round(row), column, garbage_frame, negative=True)
        row = row + speed
        obstacle.row = round(row)
