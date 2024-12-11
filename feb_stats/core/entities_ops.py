import numpy as np
import pandas as pd

from feb_stats.core.entities import Boxscore, Game, League, Team
from feb_stats.core.utils import get_averageable_numerical_columns


# TODO: These ops should be done in a DB
def get_team_by_name(league: League, team_name: str) -> Team:
    """Retrieves a team by name from a league.
    :param league: League to retrieve from.
    :param team_name: Name of the team to retrieve.
    :return: The retrieved team.
    """
    for team in league.teams:
        if team.name == team_name:
            return team
    raise Exception(f"Unable to find the team {team_name} in the league {league}")


def get_games_by_team(league: League, team: Team) -> list[Game]:
    """Retrieves all the games played by a team in a league.
    :param league: League to retrieve from.
    :param team: Team whose games will be retrieved.
    :return: List of games played by `team`.
    """
    matching_games = []
    for game in league.games:
        if team in {game.home_team, game.away_team}:
            matching_games.append(game)
    return matching_games


def get_team_boxscores(league: League, team: Team) -> list[Boxscore]:
    """Retrieves the boxscores of a team from a league.
    :param league: League to retrieve from.
    :param team: Team whose boxscores will be retrieved.
    :return: List of boxscores of `team`.
    """
    return [
        game.home_boxscore if game.home_team == team else game.away_boxscore for game in get_games_by_team(league, team)
    ]


def get_rival_boxscores(league: League, team: Team) -> list[Boxscore]:
    """Retrieves the boxscores of the rivals of a team from a league.
    :param league: League to retrieve from.
    :param team: Team whose rival boxscores will be retrieved.
    :return: List of boxscores of the rivals of  `team`.
    """
    return [
        game.home_boxscore if game.home_team != team else game.away_boxscore for game in get_games_by_team(league, team)
    ]


def average_games(df: pd.DataFrame, individual_columns: bool = False) -> pd.DataFrame:
    """Average statistics dataframes.
    :param df: Dataframe.
    :param individual_columns: Whether we are averaging individual columns or not.
    :return: Averaged dataframe.
    """
    n_games = df.loc[:, "games"].astype(np.float32)
    df.loc[:, get_averageable_numerical_columns(individual_columns=individual_columns)] = (
        df.loc[:, get_averageable_numerical_columns(individual_columns=individual_columns)]
        .astype(np.float32)
        .div(n_games, axis="rows")
    )
    if "minutes" in df:
        df.loc[:, "minutes"] /= n_games
    df.loc[:, "mode"] = "Media"
    return df
