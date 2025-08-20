import os
from pathlib import Path

from django.conf import settings


def read_file(filename: str) -> bytes:
    with open(filename, mode="rb") as f:
        read_f = f.read()
    return read_f


def get_boxscore_files() -> list[str]:
    return [
        str(file)
        for extension in settings.ALLOWED_FILE_EXTENSIONS
        for file in Path(settings.UPLOAD_FOLDER).glob(f"*.{extension}")
    ]


def read_boxscores_from_files() -> list[bytes]:
    return [read_file(filename) for filename in get_boxscore_files()]


def remove_boxscore_files() -> None:
    for filename in get_boxscore_files():
        os.remove(filename)


def is_allowed_file_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in settings.ALLOWED_FILE_EXTENSIONS
