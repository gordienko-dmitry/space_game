from itertools import cycle
from pathlib import Path
from typing import List
import curses

import eventloop

from .curses_tools import draw_frame, get_frame_size, read_controls, Window
from .settings import MODELS_PATH
from .frames import read_frame
from .stars import blink_star
from .ship import Ship


SPACE_PRESSED: bool = False


def menu(canvas: Window) -> None:
    """Preparing game field, creating all objects, starting game loop."""
    curses.curs_set(False)
    canvas.nodelay(True)

    title_path: Path = MODELS_PATH.joinpath("start_game")
    game_title_frames: List[str] = [read_frame(title_path.joinpath(f"{word}.txt")) for word in "starwar"]
    border_frame: str = read_frame(title_path.joinpath("border.txt"))

    height: int
    width: int
    height_border_frame: int
    width_border_frame: int
    height, width = canvas.getmaxyx()
    height_border_frame, width_border_frame = get_frame_size(border_frame)
    ship_window: Window = canvas.derwin(height_border_frame + 2, width_border_frame + 2,
                                        round(height/2 - height_border_frame - 1),
                                        round(width / 2 - width_border_frame / 2))

    canvas.addstr(height - 2, int(width / 2 - 10), "PRESS SPACE FOR START")

    ship: Ship = Ship(ship_window)
    draw_frame(ship_window, 1, 1, border_frame)
    eventloop.add_coroutine(show_title(canvas, game_title_frames, height, width))
    eventloop.add_coroutine(ship.animate(2, round(width_border_frame / 2 - 1)))
    eventloop.add_coroutine(blink_star(ship_window, 30))
    eventloop.add_coroutine(wait_for_space(canvas))
    eventloop.loop_forever([canvas, ship_window])


async def show_title(canvas: Window, frames: List[str], height: int, width: int) -> None:
    """Draw game title words."""
    height_frame: int
    width_frame: int
    height_frame, width_frame = get_frame_size(frames[0])
    row: int = round(height/2)
    column: int = round(width/2 - 3.5 * width_frame)
    for index in cycle(range(len(frames))):
        frame: str = frames[index]
        draw_frame(canvas, row, column + index * width_frame, frame, negative=True)
        await eventloop.sleep(10)
        draw_frame(canvas, row, column + index * width_frame, frame)
        await eventloop.sleep(2)


async def wait_for_space(canvas: Window) -> None:
    """Reading controls, if space - go on."""
    global SPACE_PRESSED
    space: bool
    while True:
        _, _, space = read_controls(canvas)
        if space:
            raise eventloop.LoopEnd
        await eventloop.sleep(1)
