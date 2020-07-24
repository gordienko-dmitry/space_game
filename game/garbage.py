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


garbage_frames: list = [frame for frame in read_frames_from_folder(GARBAGE_PATH)]
obstacles_in_last_collisions: list = []
obstacles: list = []


def clean_field(canvas: Window) -> None:
    """Destroy all garbage objects & clean their view. """
    obstacles_in_last_collisions.clear()
    for obstacle in obstacles:
        draw_frame(canvas, obstacle.row, obstacle.column, obstacle.frame, negative=True)
    obstacles.clear()


def _find_place_for_garbage(width: int, frame: str) -> int:
    """Finding column without collision for new garbage object."""
    frame_height: int
    frame_width: int
    column: int

    frame_height, frame_width = get_frame_size(frame)
    for _ in range(10):
        column = random.randint(1, width)
        if not any(obstacle.has_collision(1, column, frame_height, frame_width) for obstacle in obstacles):
            return column
    return 0


async def fill_orbit_with_garbage(canvas: Window) -> None:
    """Add garbage to window every tics count."""
    width: int

    _, width = getmaxyx_border(canvas)
    while True:
        tics: Union[int, None] = get_garbage_delay_tics()
        if tics is None:
            await eventloop.sleep(1)
            continue
        await eventloop.sleep(tics)

        frame: str = random.choice(garbage_frames)
        column: int = _find_place_for_garbage(width, frame)
        if column:
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

    obstacles.append(obstacle)

    while row < rows_number:
        if obstacle not in obstacles:
            break
        if obstacle in obstacles_in_last_collisions:
            obstacles_in_last_collisions.remove(obstacle)
            obstacles.remove(obstacle)
            await explode(canvas, round(row + height / 2), round(column + width / 2))
            break
        draw_frame(canvas, round(row), column, garbage_frame)
        await eventloop.sleep(1)
        draw_frame(canvas, round(row), column, garbage_frame, negative=True)
        row = row + speed
        obstacle.row = round(row)
    else:
        obstacles.remove(obstacle)
