import curses

import eventloop

from .curses_tools import draw_frame, get_frame_size, Window


EXPLOSION_FRAMES = [
    """\
           (_) 
       (  (   (  (
      () (  (  )
        ( )  ()
    """,
    """\
           (_) 
       (  (   (   
         (  (  )
          )  (
    """,
    """\
            (  
          (   (   
         (     (
          )  (
    """,
    """\
            ( 
              (
            (  
    """,
]


async def explode(canvas: Window, center_row: int, center_column: int) -> None:
    """Boom animation."""
    rows: int
    columns: int

    rows, columns = get_frame_size(EXPLOSION_FRAMES[0])
    corner_row = int(center_row - rows / 2)
    corner_column = int(center_column - columns / 2)

    curses.beep()
    for frame in EXPLOSION_FRAMES:
        draw_frame(canvas, corner_row, corner_column, frame)
        await eventloop.sleep(1)
        draw_frame(canvas, corner_row, corner_column, frame, negative=True)
        await eventloop.sleep(1)
