import pandas as pd
from python.feb_stats.transforms import oer_from_dataframe

def transform_cum_stats_shots(shots_series: pd.Series,
                              prefix='tiros') -> pd.DataFrame:
    """Shots with the format made-attempted"""
    return pd.DataFrame(shots_series.str.split('-').tolist(),
                        columns=[f'{prefix}_metidos', f'{prefix}_intentados'],
                        dtype='float32')


def transform_cum_stats_blocks(blocks_serie: pd.Series,
                               prefix='tapones') -> pd.DataFrame:
    """Blocks with the format made/received"""

    return pd.DataFrame(blocks_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_favor', f'{prefix}_contra'],
                        dtype='float32')


def transform_cum_stats_fouls(fouls_serie: pd.Series,
                              prefix='faltas') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(fouls_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_cometidas', f'{prefix}_recibidas'],
                        dtype='float32')


def transform_cum_stats_rebounds(rebs_serie: pd.Series,
                                 prefix='rebotes') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(rebs_serie.str.split('/').tolist(),
                        columns=[f'{prefix}_defensivos',
                                 f'{prefix}_ofensivos',
                                 f'{prefix}_totales',
                                 ],
                        dtype='float32')

def parse_cum_stats_df(initial_df: pd.DataFrame) -> pd.DataFrame:
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
        '2 puntos': ('2_puntos', transform_cum_stats_shots),
        '3 puntos': ('3_puntos', transform_cum_stats_shots),
        'T.Camp': ('tiros_campo', transform_cum_stats_shots),
        'T.L': ('tiros_libres', transform_cum_stats_shots),
        'RebotesDOT': ('rebotes', transform_cum_stats_rebounds),
        'FaltasCR': ('faltas', transform_cum_stats_fouls),
        'TaponesFaCo': ('tapones', transform_cum_stats_blocks),
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df.loc[:, transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis='columns',
                     labels=transform_key)
    df = oer_from_dataframe(df)
    return df

