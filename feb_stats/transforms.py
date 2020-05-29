import pandas as pd


def transform_shots(shots_series: pd.Series,
                    prefix='tiros') -> pd.DataFrame:
    """Shots with the format made-attempted"""
    return pd.DataFrame(shots_series.str.split('-').tolist(),
                        columns=[f'{prefix}_metidos', f'{prefix}_intentados'],
                        dtype='float32')


def transform_blocks(blocks_serie: pd.Series,
                     prefix='tapones') -> pd.DataFrame:
    """Blocks with the format made/received"""

    return pd.DataFrame(blocks_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_favor', f'{prefix}_contra'],
                        dtype='float32')


def transform_fouls(fouls_serie: pd.Series,
                    prefix='faltas') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(fouls_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_cometidas', f'{prefix}_recibidas'],
                        dtype='float32')


def transform_rebounds(rebs_serie: pd.Series,
                       prefix='rebotes') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(rebs_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_defensivos',
                                 f'{prefix}_ofensivos',
                                 f'{prefix}_totales',
                                 ],
                        dtype='float32')


def compute_oer(df):
    """OER = scored points / total possessions"""
    if 'posesiones_totales' not in df:
        df = compute_total_possessions(df)
    df['oer'] = df['puntos_favor'] / df['posesiones_totales']
    return df


def compute_total_possessions(df):
    """Estimation of total possessions:
        attempted shots (FG) + attempted FT / 2 + turnovers """
    df['posesiones_totales'] = df['tiros_campo_intentados'] + (df['tiros_libres_intentados'] / 2) + df['perdidas']
    return df


def parse_df(initial_df: pd.DataFrame) -> pd.DataFrame:
    no_transform_keys = {'Equipo': 'equipo',
                         'Part': 'partidos',
                         'Min': 'minutos',
                         'Ptos': 'puntos_favor',
                         'As': 'asistencias',
                         'B.P': 'perdidas',
                         'B.R': 'robos',
                         'Mat': 'mates',
                         'Val': 'valoracion',
                         }

    df = initial_df.rename(no_transform_keys,
                           axis='columns')

    transform_keys = {
        # key, Dict[new_key_prefix, function]
        '2 puntos': ('2_puntos', transform_shots),
        '3 puntos': ('3_puntos', transform_shots),
        'T.Camp': ('tiros_campo', transform_shots),
        'T.L': ('tiros_libres', transform_shots),
        'RebotesDOT': ('rebotes', transform_rebounds),
        'FaltasCR': ('faltas', transform_fouls),
        'TaponesFaCo': ('tapones', transform_blocks),
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df[transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis='columns',
                     labels=transform_key)
    df = compute_oer(df)
    return df

# El DER es el OER de los rivales cuando se enfrentan a ti
