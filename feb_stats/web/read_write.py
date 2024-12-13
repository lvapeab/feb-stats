import os
from pathlib import Path

from feb_stats.scrapers.boxscore_scraper import BoxscoreScraper

ALLOWED_FILE_EXTENSIONS = ["html", "htm"]


def read_file(filename: str) -> bytes:
    with open(filename, mode="rb") as f:
        read_f = f.read()
    return read_f


def get_boxscore_files(config: dict[str, str]) -> list[str]:
    return [
        str(file)
        for extension in ALLOWED_FILE_EXTENSIONS
        for file in Path(config["UPLOAD_FOLDER"]).glob(f"*.{extension}")
    ]


def read_boxscores_from_files(config: dict[str, str]) -> list[bytes]:
    return [read_file(filename) for filename in get_boxscore_files(config)]


def remove_boxscore_files(config: dict[str, str]) -> None:
    for filename in get_boxscore_files(config):
        os.remove(filename)


def is_allowed_file_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


def read_boxscores_from_calendar_url(
    calendar_url: str,
    season: str | None = None,
    group_id: str | None = None,
) -> list[bytes]:
    """Scrapes boxscores as HTML files going through a calendar URL.
    :param calendar_url: The calendar URL.
    :return: a list of HTML files containing boxscores.
    """
    scraper = BoxscoreScraper()
    return scraper.fetch_boxscores(calendar_url, season, group_id)
