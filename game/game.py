import curses

import eventloop

from .curses_tools import Window
from .game_scenario import show_head_stats, new_year
from .garbage import fill_orbit_with_garbage
from .stars import blink_star
from .start_menu import menu
from .ship import Ship


def launch(canvas: Window) -> None:
    """Launch game with main menu and than start game process."""
    curses.curs_set(False)
    canvas.nodelay(True)

    menu(canvas)
    canvas.clear()

    start_game(canvas)


def start_game(canvas: Window) -> None:
    """Preparing game field, creating all objects, starting game loop."""
    height: int
    width: int

    height, width = canvas.getmaxyx()
    stat_height_rows: int = 7

    head_window: Window = canvas.derwin(1, width, 0, 0)
    stat_window: Window = canvas.derwin(stat_height_rows, width, height - stat_height_rows, 0)
    space_window: Window = canvas.derwin(height - stat_height_rows, width, 1, 0)
    space_window.border()

    ship: Ship = Ship(space_window)
    eventloop.add_coroutine(ship.fly())
    eventloop.add_coroutine(ship.animate())
    eventloop.add_coroutine(show_head_stats(head_window, stat_window, ship))
    eventloop.add_coroutine(blink_star(space_window))

    eventloop.add_coroutine(fill_orbit_with_garbage(space_window))
    eventloop.add_coroutine(new_year())

    curses.beep()
    eventloop.loop_forever([head_window, space_window, stat_window])
