import pandas as pd
from typing import List
import json
from base64 import b64decode
from openpyxl import load_workbook
from io import BytesIO

def timedelta_to_str(timedelta: pd.Timedelta) -> str:
    minutes = timedelta.components.days * 24 * 60 + timedelta.components.hours * 60 + timedelta.components.minutes
    return f'{minutes:03d}:{timedelta.components.seconds:02d}'


def timedelta_to_minutes(timedelta: pd.Timedelta) -> float:
    seconds = timedelta.components.days * 24 * 60 * 60 + timedelta.components.hours * 60 * 60 + timedelta.components.minutes * 60 + timedelta.components.seconds
    minutes = seconds / 60.
    return minutes


def get_sorted_list_of_columns(individual_columns: bool = False) -> List[str]:
    """Returns a list of columns to export in the xlsx file in that order."""

    column_list = ['oer',
                   'games',
                   'points_made',
                   'total_possessions',
                   'minutes',
                   'assists',
                   'steals',
                   'turnovers',
                   '2_point_percentage',
                   '2_point_made',
                   '2_point_attempted',
                   '3_point_percentage',
                   '3_point_made',
                   '3_point_attempted',
                   'field_goal_percentage',
                   'field_goal_made',
                   'field_goal_attempted',
                   'free_throw_percentage',
                   'free_throw_made',
                   'free_throw_attempted',
                   'offensive_rebounds',
                   'defensive_rebounds',
                   'total_rebounds',
                   'fouls_made',
                   'fouls_received',
                   'blocks_made',
                   'blocks_received',
                   'dunks',
                   'ranking',
                   'point_balance',
                   ]
    if not individual_columns:
        column_list.insert(0, 'team')
        column_list.insert(2, 'der')
        column_list.insert(4, 'points_received')
        column_list.insert(-1, 'mode')
    else:
        column_list.insert(3, 'points_made_volume')
        column_list.insert(5, 'total_points_volume')
        column_list.insert(11, '2_point_made_volume')
        column_list.insert(13, '2_point_attempted_volume')
        column_list.insert(16, '3_point_made_volume')
        column_list.insert(18, '3_point_attempted_volume')
        column_list.insert(21, 'field_goal_made_volume')
        column_list.insert(23, 'field_goal_attempted_volume')
        column_list.insert(26, 'free_throw_made_volume')
        column_list.insert(28, 'free_throw_attempted_volume')
        column_list.insert(31, 'offensive_rebounds_volume')
        column_list.insert(33, 'defensive_rebounds_volume')
        column_list.insert(35, 'total_rebounds_volume')

        # TODO: this
        column_list.insert(1, 'oer_40_min')

    return column_list


def get_averageable_numerical_columns(individual_columns: bool = False) -> List[str]:
    """List of numerical columns that makes sense to average across multiple games. """
    column_list = [
        'games',
        'total_possessions',
        'points_made',
        'assists',
        'steals',
        'turnovers',
        '2_point_made',
        '2_point_attempted',
        '3_point_made',
        '3_point_attempted',
        'field_goal_made',
        'field_goal_attempted',
        'free_throw_made',
        'free_throw_attempted',
        'offensive_rebounds',
        'defensive_rebounds',
        'total_rebounds',
        'fouls_made',
        'fouls_received',
        'blocks_made',
        'blocks_received',
        'dunks',
        'ranking',
        'point_balance'
    ]
    if not individual_columns:
        column_list.append('points_received')
    return column_list


def response_to_excel(response: str,
                      output: str) -> None:
    """Exports the response of the server into xls workbook."""
    with open(response, mode='rb') as f:
        response = json.load(f)
    xls_file = b64decode(response['sheet'])
    workbook = load_workbook(filename=BytesIO(xls_file))
    workbook.save(output)
    return
