import curses

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from _curses import _CursesWindow
    Window = _CursesWindow
else:
    from typing import Any
    Window = Any

SPACE_KEY_CODE: int = 32
LEFT_KEY_CODE: int = 260
RIGHT_KEY_CODE: int = 261
UP_KEY_CODE: int = 259
DOWN_KEY_CODE: int = 258


def getmaxyx_border(canvas: Window) -> Tuple[int, int]:
    """Returns height and width of the window with border."""
    height, width = canvas.getmaxyx()
    return height - 1, width - 1


def read_controls(canvas: Window) -> Tuple[int, int, bool]:
    """Read keys pressed and returns tuple with controls state."""
    rows_direction: int = 0
    columns_direction: int = 0
    space_pressed: bool = False

    while True:
        pressed_key_code: int = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True
    
    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas: Window, start_row: int, start_column: int, text: str, negative: bool = False,
               bold: bool = False) -> None:
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""
    rows_number: int
    columns_number: int
    rows_start: int
    columns_start: int
    row: int
    column: int
    line: str
    symbol: str

    rows_number, columns_number = getmaxyx_border(canvas)
    rows_start, columns_start = 1, 1

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < rows_start:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 1:
                continue

            if column >= columns_number:
                break
                
            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol, curses.A_BOLD if bold else 0)


def get_frame_size(text: str) -> Tuple[int, int]:
    """Calculate size of multiline text fragment, return pair — number of rows and columns."""
    lines: list = text.splitlines()
    rows: int = len(lines)
    columns: int = max([len(line) for line in lines])
    return rows, columns
