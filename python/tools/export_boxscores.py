from argparse import ArgumentParser
from base64 import b64decode
from openpyxl import load_workbook
from io import BytesIO

from python.feb_stats.transforms import export_boxscores_from_path


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Boxscore analysis')
    parser.add_argument('--data', action='store', type=str, dest='data')
    parser.add_argument('--output', action='store', type=str, dest='output')

    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()
    excel_data = export_boxscores_from_path(args.data)
    wb = load_workbook(filename=BytesIO(excel_data))
    wb.save(args.output)
    exit(0)
