import functools
import numpy as np
import pandas as pd
from python.feb_stats.entities import League, Team, Boxscore
from python.feb_stats.entities_ops import get_rival_boxscores, get_team_boxscores
from python.feb_stats.utils import timedelta_to_minutes

from typing import List


def oer_from_dataframe(df: pd.DataFrame,
                       key_name='oer') -> pd.DataFrame:
    """OER = scored points / total possessions"""
    if 'total_possessions' not in list(df.index):
        df = compute_total_possessions(df)
    df.loc[:, key_name] = df.loc[:, 'points_made'] / df.loc[:, 'total_possessions']
    df.loc[:, f'{key_name}_40_min'] = 40 * df.loc[:, key_name].divide(
        df.loc[:, 'minutes'].apply(lambda x: timedelta_to_minutes(x) if not pd.isnull(x) else np.nan),
        fill_value=-1)
    return pd.DataFrame(df)


def compute_total_possessions(df: pd.DataFrame) -> pd.DataFrame:
    """Estimation of total possessions:
        attempted shots (FG) + attempted FT / 2 + turnovers """

    total_index = df.index.isin(['Total'])

    df.loc[:, 'total_possessions'] = df.loc[:, 'field_goal_attempted'] + \
                                      df.loc[:, 'free_throw_attempted'] / 2 + \
                                      df.loc[:, 'turnovers']
    df.loc[~total_index, 'total_possessions'] += df.loc[~total_index, 'assists']
    return df


def compute_oer(boxscore: pd.DataFrame
                ) -> pd.DataFrame:
    oer = oer_from_dataframe(boxscore)
    return oer


def compute_shots_percentage(df: pd.DataFrame) -> pd.DataFrame:
    """Compute FG%, 3PT% and FT%"""
    df.loc[:, '2_point_percentage'] = df.loc[:, '2_point_made'].divide(df.loc[:, '2_point_attempted'], fill_value=0.) * 100.
    df.loc[:, '3_point_percentage'] = df.loc[:, '3_point_made'].divide(df.loc[:, '3_point_attempted'], fill_value=0.) * 100.
    df.loc[:, 'field_goal_percentage'] = df.loc[:, 'field_goal_made'].divide(df.loc[:, 'field_goal_attempted'], fill_value=0.) * 100.
    df.loc[:, 'free_throw_percentage'] = df.loc[:, 'free_throw_made'].divide(df.loc[:, 'free_throw_attempted'], fill_value=0.) * 100.
    return df


def compute_volumes(df: pd.DataFrame) -> pd.DataFrame:
    """Compute the volume of a player w.r.t. the team."""

    volume_keys = {
        'points_made',
        'total_possessions',
        '2_point_made',
        '2_point_attempted',
        '3_point_made',
        '3_point_attempted',
        'field_goal_made',
        'field_goal_attempted',
        'free_throw_made',
        'free_throw_attempted',
        'offensive_rebounds',
        'defensive_rebounds',
        'total_rebounds',
    }
    for volume_key in volume_keys:
        df.loc[:, f'{volume_key}_volume'] = df.loc[:, volume_key].divide(df.loc['Total', volume_key],
                                                                          fill_value=0.) * 100.
    return df


def compute_der(boxscore: pd.DataFrame) -> pd.DataFrame:
    """DER is computed as the OER of the rivals when they play against `team`.
    """
    der = oer_from_dataframe(pd.DataFrame(boxscore.loc['Total', :]).T,
                             key_name='der')
    return der


def sum_boxscores(df1: pd.DataFrame,
                  df2: pd.DataFrame) -> pd.DataFrame:
    """Add the numerical statistics from two dataframes."""
    numbers1 = df1.loc[:, 'number']
    numbers2 = df2.loc[:, 'number']
    dorsales = numbers1.combine(numbers2, lambda x, y: x if pd.isna(y) else y)

    minutes1 = df1.loc[:, 'minutes']
    minutes2 = df2.loc[:, 'minutes']
    minutes_sum = minutes1.add(minutes2, fill_value=pd.to_timedelta(0.))

    df1 = df1.drop('number', axis='columns')
    df2 = df2.drop('number', axis='columns')
    df1 = df1.drop('minutes', axis='columns')
    df2 = df2.drop('minutes', axis='columns')
    df_sum = df1.add(df2, fill_value=0)
    df_sum.loc[:, 'number'] = dorsales
    df_sum.loc[:, 'minutes'] = minutes_sum
    return df_sum


def aggregate_boxscores(boxscores: List[Boxscore]) -> Boxscore:
    """Aggregate boxscores.  Set `'player'` as index."""
    all_dfs = [boxscore.boxscore.set_index('player') for boxscore in boxscores]
    agg_df = functools.reduce(lambda df1, df2: sum_boxscores(df1, df2), all_dfs)
    return Boxscore(boxscore=agg_df)


def compute_league_aggregates(league: League) -> League:
    """Aggregates the games of a League. Computes DER and OER."""
    aggregated_games_df = pd.DataFrame()
    aggregated_league_teams = list()
    for team in league.teams:
        team_boxscores = get_team_boxscores(league, team)
        own_df = aggregate_boxscores(team_boxscores)
        own_df = compute_oer(own_df.boxscore)
        own_df = compute_shots_percentage(own_df)
        own_df = compute_volumes(own_df)
        total_team_df = own_df.index.isin(['Total'])
        players_df = own_df.loc[~total_team_df, :]

        aggregated_league_teams.append(Team(
            id=team.id,
            name=team.name,
            season_stats=players_df
        )
        )

        team_df = own_df.loc['Total', :].copy()

        rivals_boxscores = aggregate_boxscores(get_rival_boxscores(league, team))
        rivals_df = compute_der(rivals_boxscores.boxscore)

        team_df.loc['der'] = rivals_df.loc['Total', 'der']
        team_df.loc['team'] = team.name
        team_df.loc['points_received'] = rivals_df.loc['Total', 'points_made']
        team_df.pop('number')
        team_df = team_df.reset_index().transpose()
        team_df.columns = team_df.loc['index']
        team_df = team_df.drop(['index'])
        aggregated_games_df = pd.concat([aggregated_games_df, team_df])

    aggregated_games_df = aggregated_games_df.reset_index()
    aggregated_games_df = aggregated_games_df.rename(columns={'index': 'mode'})

    return League(
        id=league.id,
        name=league.name,
        season=league.season,
        teams=aggregated_league_teams,
        games=league.games,
        aggregated_games=aggregated_games_df
    )