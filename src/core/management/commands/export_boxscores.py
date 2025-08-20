import json
from base64 import b64decode
from io import BytesIO
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from openpyxl import load_workbook

from src.core.analysis.saving import league_to_xlsx
from src.core.analysis.transforms import compute_league_aggregates
from src.core.parsers.parsers import FEBLivescoreParser
from src.core.scrapers.actions import read_boxscores_from_calendar_url


class Command(BaseCommand):
    help = "Export boxscores to Excel format from various sources"

    def add_arguments(self, parser: CommandParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--data", action="store", type=str, dest="data", default="protos/data.json")
        group.add_argument("--data-files", action="store", type=str, dest="data_files", nargs="*")
        group.add_argument("--calendar-url", action="store", type=str, dest="calendar_url")
        group.add_argument("--season", action="store", type=str, dest="season")
        group.add_argument("--group-id", action="store", type=str, dest="group_id")
        group.add_argument("--output", action="store", type=str, dest="output")
        return

    def export_boxscores_from_files(self, boxscores: list[str]) -> bytes:
        """Export a league to xlsx format from a list of boxscores.
        :param boxscores: The list of boxscore files to read.
        :return: xlsx file as bytes.
        """
        league = FEBLivescoreParser.parse_boxscores(boxscores, reader_fn=FEBLivescoreParser.read_link_file)
        new_league = compute_league_aggregates(league)
        return league_to_xlsx(new_league)

    def export_boxscores_from_bytes(self, boxscores: list[bytes]) -> bytes:
        """Export a league to xlsx format from a list of boxscores.
        :param boxscores: The list of boxscores to read.
        :return: xlsx file as bytes.
        """
        league = FEBLivescoreParser.parse_boxscores(boxscores, FEBLivescoreParser.read_link_bytes)
        new_league = compute_league_aggregates(league)
        return league_to_xlsx(new_league)

    def handle(self, *args: Any, **options: Any) -> None:
        if options["data_files"]:
            excel_data = self.export_boxscores_from_files(options["data_files"])
        elif options["calendar_url"] is not None:
            boxscores_bytes = read_boxscores_from_calendar_url(
                options["calendar_url"], options["season"], options["group_id"]
            )
            excel_data = self.export_boxscores_from_bytes(boxscores_bytes)
        elif options["data"] is not None:
            with open(options["data"], mode="rb") as f:
                data = json.load(f)
            excel_data = self.export_boxscores_from_bytes([b64decode(d) for d in data["boxscores"]])
        else:
            raise ValueError("Either --data, --data-files or --calendar-url must be specified.")
        wb = load_workbook(filename=BytesIO(excel_data))
        wb.save(options["output"])
        exit(0)
