import pandas as pd

def transform_cum_stats_shots(shots_series: pd.Series,
                              prefix='tiros') -> pd.DataFrame:
    """Shots with the format made-attempted"""
    split_fn = lambda x:  x.split()[0]  # Remove percentage
    return pd.DataFrame(shots_series.map(split_fn).str.split('/').tolist(),
                        columns=[f'{prefix}_metidos', f'{prefix}_intentados'],
                        dtype='float32')


def transform_cum_stats_blocks(blocks_serie: pd.Series,
                               prefix='tapones') -> pd.DataFrame:
    """Blocks with the format made/received"""

    return pd.DataFrame(blocks_serie.str.split(' ').tolist(),
                        columns=[f'{prefix}_favor', f'{prefix}_contra'],
                        dtype='float32')


def transform_cum_stats_fouls(fouls_serie: pd.Series,
                              prefix='faltas') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(fouls_serie.str.split(' ').tolist(),
                        columns=[f'{prefix}_cometidas', f'{prefix}_recibidas'],
                        dtype='float32')


def transform_cum_stats_rebounds(rebs_serie: pd.Series,
                                 prefix='rebotes') -> pd.DataFrame:
    """Fouls with the format made/received"""
    return pd.DataFrame(rebs_serie.str.split(' ').tolist(),
                        columns=[f'{prefix}_defensivos',
                                 f'{prefix}_ofensivos',
                                 f'{prefix}_totales',
                                 ],
                        dtype='float32')

def parse_game_stats_df(initial_df: pd.DataFrame,
                        local_team: bool) -> pd.DataFrame:

    if local_team:
        rebotes_str = 'Rebotes D O T'
        tapones_str = 'Tapones Fa Co'
    else:
        rebotes_str = 'Rebotes Def Of To'
        tapones_str = 'Tapones F C'

    no_transform_keys = {'N': 'dorsal',
                         'Jugador': 'jugador',
                         'Ptos': 'puntos_favor',
                         'As': 'asistencias',
                         'B.P': 'perdidas',
                         'B.R': 'robos',
                         'Mat': 'mates',
                         'Val': 'valoracion',
                         '+/-': 'mas_menos',
                         }

    df = initial_df.rename(no_transform_keys,
                           axis='columns')

    transform_keys = {
        # key, Dict[new_key_prefix, function]
        '2 pt': ('2_puntos', transform_cum_stats_shots),
        '3 pt': ('3_puntos', transform_cum_stats_shots),
        'T.Camp': ('tiros_campo', transform_cum_stats_shots),
        'T.L': ('tiros_libres', transform_cum_stats_shots),
        rebotes_str: ('rebotes', transform_cum_stats_rebounds),
        'Faltas C R': ('faltas', transform_cum_stats_fouls),
        tapones_str : ('tapones', transform_cum_stats_blocks),
    }

    for transform_key, transform_tuple in transform_keys.items():
        new_name, transform_function = transform_tuple
        new_df = transform_function(df[transform_key], prefix=new_name)
        df = pd.concat([df, new_df], axis=1)
        df = df.drop(axis='columns',
                     labels=transform_key)
    return df

