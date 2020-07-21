from pathlib import Path


def read_frame(path: Path) -> str:
    """Reading text from a file."""
    with open(str(path), "r") as my_file:
        return my_file.read()


def read_frames_from_folder(path: Path) -> list:
    """Reading all frames in txt files in folder."""
    return [read_frame(filepath) for filepath in path.glob("*.txt")]
