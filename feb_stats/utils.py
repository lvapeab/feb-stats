from typing import List


def get_sorted_list_of_columns(individual_columns: bool = False) -> List[str]:
    column_list = ['oer',
                   'partidos',
                   'posesiones_totales',
                   'minutos',
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
        column_list.insert(0, 'dorsal')

    return column_list


def numerical_columns() -> List[str]:
    return [
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
        'mas_menos'
    ]
