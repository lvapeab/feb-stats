import pandas as pd
import numpy as np
from typing import List

from python.feb_stats.entities import League, Team, Game, Boxscore
from python.feb_stats.utils import get_averageable_numerical_columns


# TODO: These ops should be done in a DB
def get_team_by_name(league: League,
                     team_name: str) -> Team:
    for team in league.teams:
        if team.name == team_name:
            return team
    raise Exception(f'Unable to find the team {team_name} in the league {league}')


def get_games_by_team(league: League,
                      team: Team) -> List[Game]:
    matching_games = []
    for game in league.games:
        if team in {game.home_team, game.away_team}:
            matching_games.append(game)
    return matching_games


def get_team_boxscores(league: League,
                       team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.home_team == team else game.away_boxscore
            for game in get_games_by_team(league, team)]


def get_rival_boxscores(league: League,
                        team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.home_team != team else game.away_boxscore
            for game in get_games_by_team(league, team)]


def average_games(df: pd.DataFrame,
                  individual_columns: bool = False) -> pd.DataFrame:
    n_games = df.loc[:, 'games'].astype(np.float32)
    df.loc[:, get_averageable_numerical_columns(individual_columns=individual_columns)] = \
        df.loc[:, get_averageable_numerical_columns(individual_columns=individual_columns)].astype(np.float32).div(n_games, axis='rows')
    if 'minutes' in df:
        df.loc[:, 'minutes'] /= n_games
    df.loc[:, 'mode'] = 'Media'
    return df