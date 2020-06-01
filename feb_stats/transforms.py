import functools
import pandas as pd
from feb_stats.entities import League, Team, Boxscore, get_games_by_team
from typing import List


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
def compute_der(league: League,
                team: Team,
                ) -> float:
    assert team in league.teams, f'The team {team} is not in the league.'
    games = get_games_by_team(league,
                              team)
    total_df = pd.DataFrame()
    for game in games:
        df = game.local_boxscore.boxscore.tail(1) if game.local_team != team else game.local_boxscore.boxscore.tail(1)
        total_df = pd.concat([total_df, df], ignore_index=True)
    der = compute_oer(total_df.sum())['oer']
    return der

def sum_boxscores(df1:pd.DataFrame, df2:pd.DataFrame) -> pd.DataFrame:
    dorsales1 = df1['dorsal']
    df_sum = pd.concat([df1, df2]).groupby('jugador', as_index=True).sum()
    df_sum['dorsal'] = dorsales1
    return df_sum


def aggregate_boxscores(boxscores: List[Boxscore]) -> Boxscore:
    all_dfs = [boxscore.boxscore.set_index('jugador') for boxscore in boxscores]
    agg_df = functools.reduce(lambda df1, df2: sum_boxscores(df1, df2), all_dfs)
    return Boxscore(id=-1,
                    boxscore=agg_df
                    )


def aggregate_league(league: League) -> League:
    """Aggregates the games of a League. Computing DER and OER."""
