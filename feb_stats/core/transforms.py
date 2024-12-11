import functools

import pandas as pd

from feb_stats.core.entities import Boxscore, League, Team
from feb_stats.core.entities_ops import get_rival_boxscores, get_team_boxscores
from feb_stats.core.utils import timedelta_to_minutes

__all__ = [
    "compute_oer",
    "compute_total_possessions",
    "compute_shots_percentage",
    "compute_volumes",
    "compute_der",
    "sum_boxscores",
    "aggregate_boxscores",
    "compute_league_aggregates",
]


def compute_oer(df: pd.DataFrame, key_name: str = "oer") -> pd.DataFrame:
    """Computes the offensive efficiency rate (OER) from a dataframe, following:
        OER = scored points / total possessions
    Also extrapolates the OER value to 40 played minutes.
    :param df: Dataframe to use.
    :param key_name: Name of the key to store the OER.
    :return: The input dataframe including oer columns.
    """
    if "total_possessions" not in list(df.index):
        df = compute_total_possessions(df)
    df.loc[:, key_name] = df.loc[:, "points_made"] / df.loc[:, "total_possessions"]
    df.loc[:, f"{key_name}_40_min"] = 40 * df.loc[:, key_name].divide(
        df.loc[:, "minutes"].apply(lambda x: timedelta_to_minutes(x) if not pd.isnull(x) else 0.0),
        fill_value=-1,
    )
    return pd.DataFrame(df)


def compute_total_possessions(df: pd.DataFrame) -> pd.DataFrame:
    """Estimates the number of possessions from a dataframe, as:
        number_of_possessions = attempted FG + attempted FT / 2 + turnovers
    If the indices of the dataframe are the players, the assists are added to the formula above .
    :param df: Dataframe to use.
    :return: Input dataframe including the `'total_possessions'` column.
    """
    total_index = df.index.isin(["Total"])

    df.loc[:, "total_possessions"] = (
        df.loc[:, "field_goal_attempted"] + df.loc[:, "free_throw_attempted"] / 2 + df.loc[:, "turnovers"]
    )
    df.loc[~total_index, "total_possessions"] += df.loc[~total_index, "assists"]
    return df


def compute_shots_percentage(df: pd.DataFrame, shot_columns: set[str] | None = None) -> pd.DataFrame:
    """Compute percentage of shots, including 2PT, 3PT, FG and FT.
    :param df: Dataframe to use.
    :param shot_columns: Prefix of the columns from which to compute percentages.
    :return: Input dataframe including the *_percentage columns.
    """
    shot_columns = shot_columns or {"2_point", "3_point", "field_goal", "free_throw"}

    for shot_column in shot_columns:
        df.loc[:, f"{shot_column}_percentage"] = (
            df.loc[:, f"{shot_column}_made"].divide(df.loc[:, f"{shot_column}_attempted"], fill_value=0.0) * 100.0
        )
    return df


def compute_volumes(df: pd.DataFrame, volume_keys: set[str] | None = None) -> pd.DataFrame:
    """Compute the volume of stats for a player w.r.t. the team. The volume is the percentage of the stat that is
    accountable to that player.
    :param df: Dataframe to use.
    :param volume_keys: Dataframe columns from which to compute volumes.
    :return: Input dataframe including the *_percentage columns.
    """

    volume_keys = volume_keys or {
        "points_made",
        "total_possessions",
        "2_point_made",
        "2_point_attempted",
        "3_point_made",
        "3_point_attempted",
        "field_goal_made",
        "field_goal_attempted",
        "free_throw_made",
        "free_throw_attempted",
        "offensive_rebounds",
        "defensive_rebounds",
        "total_rebounds",
    }
    for volume_key in volume_keys:
        df.loc[:, f"{volume_key}_volume"] = (
            df.loc[:, volume_key].divide(df.loc["Total", volume_key], fill_value=0.0) * 100.0
        )
    return df


def compute_der(df: pd.DataFrame) -> pd.DataFrame:
    """Computes the defensive efficiency rate (DER). The DER of a team is computed as the OER of the rivals when they
    play against this team
    :param df: Dataframe to use. Needs to contain the data from the rivals.
    :return: Input dataframe including the *_percentage columns.
    """
    df = compute_oer(pd.DataFrame(df.loc["Total", :]).T, key_name="der")
    return df


def sum_boxscores(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Adds two dataframes. It won't sum the `'number'` column.
    :param df1: First dataframe to add.
    :param df2: Second dataframe to add.
    :return: The sum of the dataframes.
    """
    numbers1 = df1.loc[:, "number"]
    numbers2 = df2.loc[:, "number"]
    dorsales = numbers1.combine(numbers2, lambda x, y: x if pd.isna(y) else y)

    minutes1 = df1.loc[:, "minutes"]
    minutes2 = df2.loc[:, "minutes"]
    minutes_sum = minutes1.add(minutes2, fill_value=pd.to_timedelta(0.0))

    df1 = df1.drop("number", axis="columns")
    df2 = df2.drop("number", axis="columns")
    df1 = df1.drop("minutes", axis="columns")
    df2 = df2.drop("minutes", axis="columns")
    df_sum = df1.add(df2, fill_value=0)
    df_sum.loc[:, "number"] = dorsales
    df_sum.loc[:, "minutes"] = minutes_sum
    return df_sum


def aggregate_boxscores(boxscores: list[Boxscore]) -> Boxscore:
    """Reduces a list of Boxscores by summation. Set `'player'` as the index of the output Boxscore.
    :param boxscores: List of Boxscores to sum.
    :return: A Boxscore as the sum of `boxscores`.
    """
    if not boxscores:
        raise ValueError("Boxscores cannot be empty.")
    all_dfs = [boxscore.boxscore.set_index("player") for boxscore in boxscores]
    agg_df = functools.reduce(lambda df1, df2: sum_boxscores(df1, df2), all_dfs)
    team = boxscores[0].team
    scores = sum(bs.score for bs in boxscores)
    return Boxscore(boxscore=agg_df, team=team, score=scores)


def compute_league_aggregates(league: League) -> League:
    """Aggregates the games of a League. Computes DER and OER.
    :param league: League to aggregate the results.
    :return: League with the aggregated games.
    """
    aggregated_games_df = pd.DataFrame()
    aggregated_league_teams: list[Team] = []
    for team in league.teams:
        team_boxscores = get_team_boxscores(league, team)
        own_df = aggregate_boxscores(team_boxscores)
        team_df = compute_oer(own_df.boxscore)
        team_df = compute_shots_percentage(team_df)
        team_df = compute_volumes(team_df)
        total_team_df = team_df.index.isin(["Total"])
        players_df = team_df.loc[~total_team_df, :]

        aggregated_league_teams.append(Team(name=team.name, season_stats=players_df))

        team_df = team_df.loc["Total", :].copy()

        rivals_boxscores = aggregate_boxscores(get_rival_boxscores(league, team))
        rivals_df = compute_der(rivals_boxscores.boxscore)

        team_df.loc["der"] = rivals_df.loc["Total", "der"]
        team_df.loc["team"] = team.name
        team_df.loc["points_received"] = rivals_df.loc["Total", "points_made"]
        team_df.pop("number")
        team_df = team_df.reset_index().transpose()
        team_df.columns = team_df.loc["index"]
        team_df = team_df.drop(["index"])
        aggregated_games_df = pd.concat([aggregated_games_df, team_df])

    aggregated_games_df = aggregated_games_df.reset_index()
    aggregated_games_df = aggregated_games_df.rename(columns={"index": "mode"})

    return League(
        name=league.name,
        season=league.season,
        teams=aggregated_league_teams,
        games=league.games,
        aggregated_games=aggregated_games_df,
    )
