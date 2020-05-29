import pandas as pd

def compute_oer(df: pd.DataFrame) -> pd.DataFrame:
    """OER = scored points / total possessions"""
    if 'posesiones_totales' not in df:
        df = compute_total_possessions(df)
    df['oer'] = df['puntos_favor'] / df['posesiones_totales']
    return df


def compute_total_possessions(df: pd.DataFrame) -> pd.DataFrame:
    """Estimation of total possessions:
        attempted shots (FG) + attempted FT / 2 + turnovers """
    df['posesiones_totales'] = df['tiros_campo_intentados'] + (df['tiros_libres_intentados'] / 2) + df['perdidas']
    return df
# El DER es el OER de los rivales cuando se enfrentan a ti
