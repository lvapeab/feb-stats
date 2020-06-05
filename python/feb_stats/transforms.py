import functools
import pandas as pd
from python.feb_stats.entities import League, Team, Boxscore, get_rival_boxscores, get_team_boxscores
from typing import List


def oer_from_dataframe(df: pd.DataFrame,
                       key_name='oer') -> pd.DataFrame:
    """OER = scored points / total possessions"""
    if 'posesiones_totales' not in list(df.index):
        df = compute_total_possessions(df)
    df.loc[:, key_name] = df.loc[:, 'puntos_favor'] / df.loc[:, 'posesiones_totales']
    return pd.DataFrame(df)


def compute_total_possessions(df: pd.DataFrame) -> pd.DataFrame:
    """Estimation of total possessions:
        attempted shots (FG) + attempted FT / 2 + turnovers """
    df.loc[:, 'posesiones_totales'] = df.loc[:, 'tiros_campo_intentados'] + \
                                      df.loc[:, 'tiros_libres_intentados'] / 2 + \
                                      df.loc[:, 'perdidas']
    return df


def compute_oer(boxscore: pd.DataFrame
                ) -> pd.DataFrame:
    oer = oer_from_dataframe(boxscore)
    return oer


def compute_der(boxscore: pd.DataFrame,
                ) -> pd.DataFrame:
    """DER is computed as the OER of the rivals when they play against `team`.
    """
    der = oer_from_dataframe(pd.DataFrame(boxscore.loc['Total', :]).T,
                             key_name='der')
    return der


def sum_boxscores(df1: pd.DataFrame,
                  df2: pd.DataFrame) -> pd.DataFrame:
    """Add the numerical statistics from two dataframes. Set `'jugador'` as index."""
    dorsales1 = df1.loc[:, 'dorsal']
    dorsales2 = df2.loc[:, 'dorsal']
    dorsales = dorsales1.combine(dorsales2, lambda x, y: x if pd.isna(y) else y)

    minutes1 = df1.loc[:, 'minutos']
    minutes2 = df2.loc[:, 'minutos']
    minutes_sum = minutes1.add(minutes2, fill_value=pd.to_timedelta(0.))

    df1 = df1.drop('dorsal', axis='columns')
    df2 = df2.drop('dorsal', axis='columns')
    df1 = df1.drop('minutos', axis='columns')
    df2 = df2.drop('minutos', axis='columns')
    df_sum = df1.add(df2, fill_value=0)
    df_sum.loc[:, 'dorsal'] = dorsales
    df_sum.loc[:, 'minutos'] = minutes_sum
    return df_sum


def aggregate_boxscores(boxscores: List[Boxscore]) -> Boxscore:
    all_dfs = [boxscore.boxscore.set_index('jugador') for boxscore in boxscores]
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
        bad_df = own_df.index.isin(['Total'])
        players_df = own_df.loc[~bad_df, :]

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
        team_df.loc['equipo'] = team.name
        team_df.loc['puntos_contra'] = rivals_df.loc['Total', 'puntos_favor']
        team_df.pop('dorsal')
        team_df = team_df.reset_index().transpose()
        team_df.columns = team_df.loc['index']
        team_df = team_df.drop(['index'])
        aggregated_games_df = pd.concat([aggregated_games_df, team_df])

    aggregated_games_df = aggregated_games_df.reset_index()
    aggregated_games_df = aggregated_games_df.rename(columns={'index': 'modo'})

    return League(
        id=league.id,
        name=league.name,
        season=league.season,
        teams=aggregated_league_teams,
        games=league.games,
        aggregated_games=aggregated_games_df
    )
