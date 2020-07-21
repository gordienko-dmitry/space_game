from typing import Union, Tuple, Iterable, List
import curses

import eventloop

from .curses_tools import draw_frame, Window


class Obstacle:

    def __init__(self, row: int, column: int, frame: str, rows_size: int = 1, columns_size: int = 1,
                 uid: Union[int, None] = None) -> None:
        self.row: int = row
        self.column: int = column
        self.rows_size: int = rows_size
        self.columns_size: int = columns_size
        self.uid: Union[int, None] = uid
        self.frame: str = frame

    def get_bounding_box_frame(self) -> str:
        """Increment box size to compensate obstacle movement."""
        rows: int
        columns: int

        rows, columns = self.rows_size + 1, self.columns_size + 1
        return '\n'.join(_get_bounding_box_lines(rows, columns))

    def get_bounding_box_corner_pos(self) -> Tuple[int, int]:
        """Getting up + left corner of bounding box."""
        return self.row - 1, self.column - 1

    def dump_bounding_box(self) -> Tuple[int, int, str]:
        """Get size and coords of bounding box."""
        row, column = self.get_bounding_box_corner_pos()
        return row, column, self.get_bounding_box_frame()

    def has_collision(self, obj_corner_row: int, obj_corner_column: int, obj_size_rows: int = 1,
                      obj_size_columns: int = 1) -> bool:
        """Determine if collision has occurred. Return True or False."""
        return has_collision(
            (self.row, self.column),
            (self.rows_size, self.columns_size),
            (obj_corner_row, obj_corner_column),
            (obj_size_rows, obj_size_columns),
        )


def _get_bounding_box_lines(rows: int, columns: int) -> Iterable[str]:
    """Generator rows of bounding box view around garbage frame."""
    yield ' ' + '-' * columns + ' '
    for _ in range(rows):
        yield '|' + ' ' * columns + '|'
    yield ' ' + '-' * columns + ' '


async def show_obstacles(canvas: Window, obstacles: List[Obstacle]) -> None:
    """Display bounding boxes of every obstacle in a list"""

    while True:
        boxes: List[Tuple[int, int, str]] = []

        for obstacle in obstacles:
            boxes.append(obstacle.dump_bounding_box())

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame)

        await eventloop.sleep(1)

        for row, column, frame in boxes:
            draw_frame(canvas, row, column, frame, negative=True)


def _is_point_inside(corner_row: int, corner_column: int, size_rows: int, size_columns: int,
                     point_row: int, point_row_column: int) -> bool:
    """Find out if point inside figure."""
    rows_flag: bool = corner_row <= point_row < corner_row + size_rows
    columns_flag: bool = corner_column <= point_row_column < corner_column + size_columns

    return rows_flag and columns_flag


def has_collision(obstacle_corner: Tuple[int, int], obstacle_size: Tuple[int, int], obj_corner: Tuple[int, int],
                  obj_size: Tuple[int, int] = (1, 1)) -> bool:
    """Determine if collision has occured. Return True or False."""

    opposite_obstacle_corner: Tuple[int, int] = (
        obstacle_corner[0] + obstacle_size[0] - 1,
        obstacle_corner[1] + obstacle_size[1] - 1,
    )

    opposite_obj_corner: Tuple[int, int] = (
        obj_corner[0] + obj_size[0] - 1,
        obj_corner[1] + obj_size[1] - 1,
    )

    return any([
        _is_point_inside(*obstacle_corner, *obstacle_size, *obj_corner),
        _is_point_inside(*obstacle_corner, *obstacle_size, *opposite_obj_corner),

        _is_point_inside(*obj_corner, *obj_size, *obstacle_corner),
        _is_point_inside(*obj_corner, *obj_size, *opposite_obstacle_corner),
    ])
