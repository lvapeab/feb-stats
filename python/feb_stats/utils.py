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
                   'partidos',
                   'puntos_favor',
                   'posesiones_totales',
                   'minutos',
                   'asistencias',
                   'robos',
                   'perdidas',
                   'porcentaje_2_puntos',
                   '2_puntos_metidos',
                   '2_puntos_intentados',
                   'porcentaje_3_puntos',
                   '3_puntos_metidos',
                   '3_puntos_intentados',
                   'porcentaje_tiros_campo',
                   'tiros_campo_metidos',
                   'tiros_campo_intentados',
                   'porcentaje_tiros_libres',
                   'tiros_libres_metidos',
                   'tiros_libres_intentados',
                   'rebotes_defensivos',
                   'rebotes_ofensivos',
                   'rebotes_totales',
                   'faltas_cometidas',
                   'faltas_recibidas',
                   'tapones_favor',
                   'tapones_contra',
                   'mates',
                   'valoracion',
                   'mas_menos',
                   ]
    if not individual_columns:
        column_list.insert(0, 'equipo')
        column_list.insert(2, 'der')
        column_list.insert(4, 'puntos_contra')
        column_list.insert(-1, 'modo')
    else:
        column_list.insert(3, 'volumen_puntos_favor')
        column_list.insert(5, 'volumen_posesiones_totales')
        column_list.insert(11, 'volumen_2_puntos_metidos')
        column_list.insert(13, 'volumen_2_puntos_intentados')
        column_list.insert(16, 'volumen_3_puntos_metidos')
        column_list.insert(18, 'volumen_3_puntos_intentados')
        column_list.insert(21, 'volumen_tiros_campo_metidos')
        column_list.insert(23, 'volumen_tiros_campo_intentados')
        column_list.insert(26, 'volumen_tiros_libres_metidos')
        column_list.insert(28, 'volumen_tiros_libres_intentados')
        column_list.insert(31, 'volumen_rebotes_defensivos')
        column_list.insert(33, 'volumen_rebotes_ofensivos')
        column_list.insert(35, 'volumen_rebotes_totales')

        # TODO: this
        column_list.insert(1, 'oer_por_40_minutos')

    return column_list


def get_averageable_numerical_columns(individual_columns: bool = False) -> List[str]:
    """List of numerical columns that makes sense to average across multiple games. """
    column_list = [
        'partidos',
        'posesiones_totales',
        'puntos_favor',
        'asistencias',
        'robos',
        'perdidas',
        '2_puntos_metidos',
        '2_puntos_intentados',
        '3_puntos_metidos',
        '3_puntos_intentados',
        'tiros_campo_metidos',
        'tiros_campo_intentados',
        'tiros_libres_metidos',
        'rebotes_defensivos',
        'rebotes_ofensivos',
        'rebotes_totales',
        'faltas_cometidas',
        'faltas_recibidas',
        'tapones_favor',
        'tapones_contra',
        'mates',
        'valoracion',
        'mas_menos'
    ]
    if not individual_columns:
        column_list.append('puntos_contra')
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
