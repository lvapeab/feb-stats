import json
from argparse import ArgumentParser
from base64 import b64decode
from openpyxl import load_workbook
from io import BytesIO


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Boxscore analysis')
    parser.add_argument('--response', action='store', type=str, dest='response')
    parser.add_argument('--output', action='store', type=str, dest='output')

    return parser


if __name__ == '__main__':
    args = get_parser().parse_args()

    with open(args.response, mode='rb') as f:
        o = json.load(f)
    xlsx_data = o['sheet']
    input_excel = b64decode(xlsx_data)

    wb = load_workbook(filename=BytesIO(input_excel))
    wb.save(args.output)
    exit(0)