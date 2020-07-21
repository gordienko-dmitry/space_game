import curses

from game import launch


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(launch)
