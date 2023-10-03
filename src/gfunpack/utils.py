import os
import pathlib


def check_directory(directory: str, create: bool = False) -> pathlib.Path:
    d = pathlib.Path(directory)
    if not d.exists() and create:
        os.makedirs(d)
    if not d.exists() or not d.is_dir():
        raise ValueError(f'{d} is not a valid directory')
    return d
