import json
from base64 import b64decode
from argparse import ArgumentParser

from openpyxl import load_workbook
from io import BytesIO

from python.feb_stats.entities_ops import export_boxscores_from_bytes


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
