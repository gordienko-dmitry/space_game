from typing import Tuple, Union
from itertools import cycle
import curses
import time

import eventloop

from .curses_tools import draw_frame, get_frame_size, read_controls, getmaxyx_border, Window
from .garbage import obstacles, explode, clean_field
from .game_scenario import show_game_over
from .settings import MODELS_PATH
from .physics import update_speed
from .frames import read_frame
from .fire import fire


class Ship:
    """Ship object."""

    def __init__(self, canvas: Window) -> None:
        self.canvas: Window = canvas
        self.row: int = 0
        self.column: int = 0
        self.row_speed: float = 0.0
        self.column_speed: float = 0.0
        self.dead: bool = False
        self.lives: int = 3

        frame1: str = read_frame(MODELS_PATH.joinpath("rocket", "rocket_frame_1.txt"))
        frame2: str = read_frame(MODELS_PATH.joinpath("rocket", "rocket_frame_2.txt"))
        self.frame: str = frame1
        self.frames: list = [frame1, frame2]

        self.height: int
        self.width: int
        self.max_y: int
        self.max_x: int

        self.height, self.width = get_frame_size(frame1)
        field_height, field_width = getmaxyx_border(canvas)
        self.max_y = field_height - self.height - 1
        self.max_x = field_width - self.width - 1

    def make_controls(self, row: int, column: int) -> Tuple[int, int]:
        """If user make a turn we changing row & colls of the ship."""
        rows_direction: int
        columns_direction: int
        fire_on: bool
        rows_direction, columns_direction, fire_on = read_controls(self.canvas)

        if fire_on:
            eventloop.add_coroutine(fire(self.canvas, self.row * 1.0, self.column + self.width / 2))

        self.row_speed, self.column_speed = update_speed(self.row_speed, self.column_speed, rows_direction,
                                                         columns_direction)
        row = round(min(row + self.row_speed, self.max_y))
        row = max(1, row)
        column = round(min(column + self.column_speed, self.max_x))
        column = max(1, column)
        return row, column

    def blink_few_times_before_continue(self):
        for _ in range(5):
            draw_frame(self.canvas, self.row, self.column, self.frame)
            self.canvas.refresh()
            time.sleep(0.1)
            draw_frame(self.canvas, self.row, self.column, self.frame, negative=True)
            self.canvas.refresh()
            time.sleep(0.1)

    async def explode_ship_and_game_over(self):
        self.dead = True
        await explode(self.canvas, int(self.row + self.height / 2), int(self.column + self.width / 2))
        eventloop.add_coroutine(show_game_over(self.canvas))

    async def check_collision(self) -> None:
        """Actions if ship has collision with garbage."""
        if not any(obstacle.has_collision(self.row, self.column, self.height, self.width) for obstacle in obstacles):
            return

        self.lives -= 1
        if not self.lives:
            await self.explode_ship_and_game_over()
            return
        clean_field(self.canvas)
        self.blink_few_times_before_continue()

    async def fly(self, row: Union[int, None] = None, column: Union[int, None] = None) -> None:
        """Drawing & Replacing ship."""
        self.row = round(self.max_y / 2) if row is None else row
        self.column = round(self.max_x / 2 - self.width / 2) if column is None else column

        while True:
            await self.check_collision()
            if self.dead:
                break
            draw_frame(self.canvas, self.row, self.column, self.frame)
            await eventloop.sleep(1)
            draw_frame(self.canvas, self.row, self.column, self.frame, negative=True)
            self.row, self.column = self.make_controls(self.row, self.column)

    async def animate(self, row: Union[int, None] = None, column: Union[int, None] = None) -> None:
        """Changing ship frame every 2 tics."""
        if row:
            self.row = row
        if column:
            self.column = column
        for frame in cycle(self.frames):
            if self.dead:
                break
            self.frame = frame
            draw_frame(self.canvas, self.row, self.column, frame, bold=True)
            await eventloop.sleep(2)
            draw_frame(self.canvas, self.row, self.column, frame, negative=True)

