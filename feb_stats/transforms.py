import pandas as pd
from feb_stats.entities import League, Team, get_games_by_team


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


def cum_stats(df: pd.DataFrame) -> pd.DataFrame:
    return df.cumsum().tail(1)

# El DER es el OER de los rivales cuando se enfrentan a ti
def compute_der(league: League,
                team: Team,
                ) -> float:
    assert team in league.teams, f'The team {team} is not in the league.'
    games = get_games_by_team(league,
                              team)
    total_df = pd.DataFrame()
    for game in games:
        if game.local_team != team:
            df = game.local_boxscore.boxscore.tail(1)
        else:
            df = game.local_boxscore.boxscore.tail(1)
        total_df = pd.concat([total_df, df], ignore_index=True)
    cum_df = cum_stats(total_df)
    der = compute_oer(cum_df)['oer']
    return der
