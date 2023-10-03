import pathlib


def check_directory(directory: str):
    d = pathlib.Path(directory)
    if not d.exists() or not d.is_dir():
        raise ValueError(f'{d} is not a valid directory')
    return d
