from typing import Union
import curses

import eventloop

from .curses_tools import draw_frame, getmaxyx_border, get_frame_size, Window
from .settings import MODELS_PATH
from .frames import read_frame


GAME_OVER_TEXT: str = read_frame(MODELS_PATH.joinpath("game_over.txt"))
YEAR: int = 1957

PHRASES: dict = {
    # Только на английском, Repl.it ломается на кириллице
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}


def get_garbage_delay_tics() -> Union[int, None]:
    """Getting new garbage objects delay via year."""
    if YEAR < 1961:
        return None
    elif YEAR < 1969:
        return 20
    elif YEAR < 1981:
        return 14
    elif YEAR < 1995:
        return 10
    elif YEAR < 2010:
        return 8
    elif YEAR < 2020:
        return 6
    else:
        return 2


async def new_year() -> None:
    """Increase YEAR variable."""
    global YEAR
    while True:
        YEAR += 1
        await eventloop.sleep(10)


async def show_head_stats(head_canvas: Window, stat_canvas: Window, ship):
    """Draw head phrase and stats at the bottom."""
    phrase: str = ""
    frame_width: int
    life_frame: str = read_frame(MODELS_PATH.joinpath("life.txt"))
    _, frame_width = get_frame_size(life_frame)
    while True:
        phrase = PHRASES.get(YEAR, phrase)
        head_canvas.addstr(0, 1, f"{YEAR}: {phrase}")
        lives: int = ship.lives
        for i in range(lives):
            draw_frame(stat_canvas, 1, 1 + i * (frame_width + 2), life_frame)
        await eventloop.sleep(1)
        head_canvas.clear()
        for i in range(lives):
            draw_frame(stat_canvas, 1, 1 + i * (frame_width + 2), life_frame, negative=True)


async def show_game_over(canvas: Window, tics_to_stop: int = 100) -> None:
    """Show game over text."""
    height: int
    width: int
    frame_height: int
    frame_width: int

    height, width = getmaxyx_border(canvas)
    frame_height, frame_width = get_frame_size(GAME_OVER_TEXT)
    while True:
        if tics_to_stop <= 0:
            raise eventloop.LoopEnd
        draw_frame(canvas, round(height / 2 - frame_height / 2), round(width / 2 - frame_width / 2), GAME_OVER_TEXT)
        await eventloop.sleep(1)
        tics_to_stop -= 1
