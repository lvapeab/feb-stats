import json
from base64 import b64decode
from openpyxl import load_workbook
from argparse import ArgumentParser
from io import BytesIO


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Boxscore analysis")
    parser.add_argument("--response", action="store", type=str, dest="response")
    parser.add_argument("--output", action="store", type=str, dest="output")
    return parser


def response_to_xls(response: str, output_name: str, xsl_key: str = "sheet") -> None:
    """Exports the server response into a xls workbook.
    :param response: Server response, as json. The xlsx is under the key `xsl_key`
    :param output_name: Name of the xls workbook to save.
    :param xsl_key: Key in the response containing the xls data.
    :return: None
    """
    with open(response, mode="rb") as f:
        response = json.load(f)
    xls_file = b64decode(response[xsl_key])
    workbook = load_workbook(filename=BytesIO(xls_file))
    workbook.save(output_name)
    return


if __name__ == "__main__":
    args = get_parser().parse_args()
    response_to_xls(args.response, args.output)
