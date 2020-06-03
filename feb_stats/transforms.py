import functools
import pandas as pd
from feb_stats.entities import League, Team, Boxscore, get_games_by_team, get_rival_boxscores, get_team_boxscores
from typing import List


def oer_from_dataframe(df: pd.DataFrame,
                       key_name='oer') -> pd.DataFrame:
    """OER = scored points / total possessions"""
    if 'posesiones_totales' not in df:
        df = compute_total_possessions(df)
    df.loc[key_name] = df.loc['puntos_favor'] / df.loc['posesiones_totales']
    return df


def compute_total_possessions(df: pd.DataFrame) -> pd.DataFrame:
    """Estimation of total possessions:
        attempted shots (FG) + attempted FT / 2 + turnovers """
    df.loc['posesiones_totales'] = df.loc['tiros_campo_intentados'] + (df.loc['tiros_libres_intentados'] / 2) + df.loc[
        'perdidas']
    return df


def compute_oer(league: League,
                team: Team,
                ) -> pd.DataFrame:
    assert team in league.teams, f'The team {team} is not in the league.'
    boxscores = get_team_boxscores(league,
                                   team)
    total_df = aggregate_boxscores(boxscores)
    oer = oer_from_dataframe(total_df.boxscore.loc['Total'])
    return oer


def compute_der(league: League,
                team: Team,
                ) -> pd.DataFrame:
    """DER is computed as the OER of the rivals when they play against `team`.
    """
    assert team in league.teams, f'The team {team} is not in the league.'
    boxscores = get_rival_boxscores(league,
                                    team)
    total_df = aggregate_boxscores(boxscores)
    der = oer_from_dataframe(total_df.boxscore.loc['Total'],
                             key_name='der')
    return der


def sum_boxscores(df1: pd.DataFrame,
                  df2: pd.DataFrame) -> pd.DataFrame:
    """Add the numerical statistics from two dataframes. Set `'jugador'` as index."""
    dorsales1 = df1.loc[:, 'dorsal']
    df_sum = pd.concat([df1, df2]).groupby('jugador', as_index=True).sum()
    df_sum.loc[:, 'dorsal'] = dorsales1
    return df_sum


def aggregate_boxscores(boxscores: List[Boxscore]) -> Boxscore:
    all_dfs = [boxscore.boxscore.set_index('jugador') for boxscore in boxscores]
    agg_df = functools.reduce(lambda df1, df2: sum_boxscores(df1, df2), all_dfs)
    return Boxscore(boxscore=agg_df)


def compute_league_aggregates(league: League) -> League:
    """Aggregates the games of a League. Computes DER and OER."""
    aggregated_games_df = pd.DataFrame()
    for team in league.teams:
        own_df = compute_oer(league,
                             team)
        rivals_df = compute_der(league,
                                team)
        own_df.loc['equipo'] = team.name
        own_df.loc['der'] = rivals_df.loc['der']
        own_df.loc['puntos_contra'] = rivals_df.loc['puntos_favor']
        own_df.pop('dorsal')
        own_df = own_df.reset_index().transpose()
        own_df.columns = own_df.loc['index']
        own_df = own_df.drop(['index'])
        aggregated_games_df = pd.concat([aggregated_games_df, own_df])
    aggregated_games_df = aggregated_games_df.reset_index()
    aggregated_games_df = aggregated_games_df.rename(columns={'index': 'modo'})

    return League(
        id=league.id,
        name=league.name,
        season=league.season,
        teams=league.teams,
        games=league.games,
        aggregated_games=aggregated_games_df
    )
