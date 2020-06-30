import json
import pandas as pd
from base64 import b64decode
from openpyxl import load_workbook
from io import BytesIO
from typing import List

from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

from python.feb_stats.entities_ops import average_games
from python.feb_stats.parsers.feb_parser import FEBParser
from python.feb_stats.transforms import compute_league_aggregates
from python.feb_stats.utils import get_sorted_list_of_columns, timedelta_to_str

def export_boxscores_from_bytes(boxscores: List[bytes]) -> bytes:
    league = FEBParser().parse_boxscores(boxscores)
    new_league = compute_league_aggregates(league)
    return league_to_excel(new_league)


def league_to_excel(league,
                    filename: str = None,
                    col_width: int = 30) -> bytes:
    filename = filename or f'{league.name}_{league.season.replace("/", "-")}.xlsx'

    # Create a Pandas Excel writer using openpyxl as the engine.
    writer = pd.ExcelWriter(filename,
                            engine='openpyxl',
                            mode='w',
                            date_format='DD-MM-YYYY'
                            )

    if league.aggregated_games is not None:
        sheet_name = f'{league.name}_{league.season.replace("/", "-")}'
        columns = get_sorted_list_of_columns()
        column_names = list(map(lambda x: ' '.join(x.capitalize().split('_')),
                                columns))

        aggregated_games = league.aggregated_games
        averaged_games = average_games(aggregated_games.copy())

        aggregated_games.loc[:, 'minutes'] = aggregated_games['minutes'].apply(
            lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
        )
        averaged_games.loc[:, 'minutes'] = averaged_games['minutes'].apply(
            lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
        )
        aggregated_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            encoding='latin1',
            header=column_names,
            sheet_name=sheet_name)

        averaged_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            encoding='latin1',
            header=column_names,
            sheet_name=sheet_name + '-medias')

        player_columns = get_sorted_list_of_columns(individual_columns=True)
        player_column_names = list(map(lambda x: ' '.join(x.capitalize().split('_')),
                                       player_columns))
        for team in league.teams:
            if team.season_stats is not None:
                aggregated_team_season_games = team.season_stats
                averaged_team_season_games = average_games(aggregated_team_season_games.copy(),
                                                           individual_columns=True
                                                           )

                aggregated_team_season_games.loc[:, 'minutes'] = aggregated_team_season_games['minutes'].apply(
                    lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
                )
                averaged_team_season_games.loc[:, 'minutes'] = averaged_team_season_games['minutes'].apply(
                    lambda x: timedelta_to_str(x) if not pd.isnull(x) else ''
                )
                aggregated_team_season_games.to_excel(
                    writer,
                    float_format="%.3f",
                    columns=player_columns,
                    header=player_column_names,
                    encoding='latin1',
                    sheet_name=team.name[:31])
                averaged_team_season_games.to_excel(
                    writer,
                    float_format="%.3f",
                    columns=player_columns,
                    header=player_column_names,
                    encoding='latin1',
                    sheet_name=f'medias - {team.name}'[:31])

        center_alignment = Alignment(horizontal='center')
        for n_sheet, (worksheet_name, worksheet) in enumerate(writer.sheets.items()):
            for row in worksheet.iter_rows():
                for cell in row:
                    cell.alignment = center_alignment

            for n_column in range(worksheet.max_column):
                worksheet.column_dimensions[
                    get_column_letter(n_column + 1)].width = 2 * col_width if n_column < 2 else col_width
        virtual_workbook = BytesIO()
        writer.book.save(virtual_workbook)
        virtual_workbook.seek(0)
        return virtual_workbook.read()


def response_to_excel(response: str,
                      output: str) -> None:
    """Exports the response of the server into xls workbook."""
    with open(response, mode='rb') as f:
        response = json.load(f)
    xls_file = b64decode(response['sheet'])
    workbook = load_workbook(filename=BytesIO(xls_file))
    workbook.save(output)
    return
