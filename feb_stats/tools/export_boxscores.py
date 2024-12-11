import json
from argparse import ArgumentParser
from base64 import b64decode
from io import BytesIO

from openpyxl import load_workbook

from feb_stats.core.saving import league_to_xlsx
from feb_stats.core.transforms import compute_league_aggregates
from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser
from feb_stats.parsers.feb_parser import FEBParser


def read_file(filename: str) -> bytes:
    with open(filename, mode="rb") as f:
        read_f = f.read()
    return read_f


def export_boxscores_from_files(boxscores: list[str]) -> bytes:
    """Export a league to xlsx format from a list of boxscores.
    :param boxscores: The list of boxscore files to read.
    :return: xlsx file as bytes.
    """
    league = FEBLivescoreParser.parse_boxscores(boxscores, reader_fn=FEBLivescoreParser.read_link_file)
    new_league = compute_league_aggregates(league)
    return league_to_xlsx(new_league)


def export_boxscores_from_bytes(boxscores: list[bytes]) -> bytes:
    """Export a league to xlsx format from a list of boxscores.
    :param boxscores: The list of boxscores to read.
    :return: xlsx file as bytes.
    """
    league = FEBParser.parse_boxscores(boxscores, FEBParser.read_link_bytes)
    new_league = compute_league_aggregates(league)
    return league_to_xlsx(new_league)


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Boxscore analysis")
    parser.add_argument("--data", action="store", type=str, dest="data", default="protos/data.json")
    parser.add_argument("--data-files", action="store", type=str, dest="data_files", nargs="*")
    parser.add_argument("--output", action="store", type=str, dest="output")

    return parser


if __name__ == "__main__":
    args = get_parser().parse_args()
    if args.data_files is not None:
        excel_data = export_boxscores_from_files(args.data_files)
    else:
        with open(args.data, mode="rb") as f:
            data = json.load(f)
        excel_data = export_boxscores_from_bytes([b64decode(d) for d in data["boxscores"]])
    wb = load_workbook(filename=BytesIO(excel_data))
    wb.save(args.output)
    exit(0)
