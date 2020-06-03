import pandas as pd
import copy
import numpy as np
from typing import List

def get_sorted_list_of_columns() -> List[str]:
    return ['equipo',
            'oer',
            'der',
            'modo',
            'partidos',
            'posesiones_totales',
            'puntos_favor',
            'puntos_contra',
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


def numerical_columns() -> List[str]:
    return ['partidos',
            'posesiones_totales',
            'puntos_favor',
            'puntos_contra',
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
            'mas_menos'
            ]


def league_to_excel(league,
                    name: str = 'stats.xlsx',
                    sheet_name='Sheet 1',
                    col_width: int = 20) -> None:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(name,
                            engine='xlsxwriter',
                            )

    if league.aggregated_games is not None:
        columns = get_sorted_list_of_columns()
        column_names = list(map(lambda x: ' '.join(x.capitalize().split('_')),
                           columns))

        averaged_games = copy.copy(league.aggregated_games)
        n_games = averaged_games.loc[:, 'partidos'].astype(np.float32)
        averaged_games.loc[:, numerical_columns()] = averaged_games.loc[:, numerical_columns()].astype(np.float32).div(
            n_games, axis='rows')
        averaged_games['modo'] = 'Media'
        league.aggregated_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            header=column_names,
            sheet_name=sheet_name)

        averaged_games.to_excel(
            writer,
            float_format="%.3f",
            columns=columns,
            header=column_names,
            sheet_name=sheet_name + '-medias')
        for worksheet_name, worksheet in writer.sheets.items():
        #     worksheet.conditional_format('C2:C8', {type': '3_color_scale'})
            worksheet.set_column(1, 1, 2 * col_width)
            worksheet.set_column(2, len(columns), col_width)
        writer.save()
