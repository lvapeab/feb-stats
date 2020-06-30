import json
from base64 import b64decode
from argparse import ArgumentParser
from openpyxl import load_workbook
from io import BytesIO
from typing import List

from python.feb_stats.parsers.feb_parser import FEBParser
from python.feb_stats.transforms import compute_league_aggregates
from python.feb_stats.saving import league_to_xlsx


def export_boxscores_from_bytes(boxscores: List[bytes]) -> bytes:
    """Export a league to xlsx format from a list of boxscores.
    :param boxscores: The list of boxscores to read.
    :return: xlsx file as bytes.
    """
    league = FEBParser().parse_boxscores(boxscores)
    new_league = compute_league_aggregates(league)
    return league_to_xlsx(new_league)


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Boxscore analysis')
    parser.add_argument('--data', action='store', type=str, dest='data',
                        default='protos/data.json')
    parser.add_argument('--output', action='store', type=str, dest='output')

    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    with open(args.data, mode='rb') as f:
        data = json.load(f)
    excel_data = export_boxscores_from_bytes([b64decode(d) for d in data['boxscores']])
    wb = load_workbook(filename=BytesIO(excel_data))
    wb.save(args.output)
    exit(0)
