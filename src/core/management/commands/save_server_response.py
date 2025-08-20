import json
from base64 import b64decode
from io import BytesIO
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from openpyxl import load_workbook


class Command(BaseCommand):
    help = "Convert server response to Excel file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--response",
            type=str,
            required=True,
            help="JSON response file from server",
        )
        parser.add_argument(
            "--output",
            type=str,
            required=True,
            help="Output Excel file path",
        )
        parser.add_argument(
            "--xls-key",
            type=str,
            default="sheet",
            help="Key in JSON response containing Excel data",
        )

    def response_to_xls(self, response_path: str, output_path: str, xls_key: str) -> None:
        """Export server response into Excel workbook.

        Args:
            response_path: Path to JSON response file
            output_path: Path where Excel file will be saved
            xls_key: Key in the response containing Excel data

        Raises:
            json.JSONDecodeError: If response file is not valid JSON
            KeyError: If xls_key is not found in response
            ValueError: If base64 decoding fails
        """
        with open(response_path, mode="rb") as f:
            response = json.load(f)

        if xls_key not in response:
            raise KeyError(f"Key '{xls_key}' not found in response")

        xls_file = b64decode(response[xls_key])
        workbook = load_workbook(filename=BytesIO(xls_file))
        workbook.save(output_path)

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            self.response_to_xls(
                response_path=options["response"],
                output_path=options["output"],
                xls_key=options["xls_key"],
            )
            self.stdout.write(self.style.SUCCESS(f"Successfully converted response to Excel file: {options['output']}"))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON file provided"))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(str(e)))
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid base64 data in response"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error converting response: {str(e)}"))
