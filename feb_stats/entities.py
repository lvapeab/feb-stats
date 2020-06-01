from typing import TypeVar, Generic, List
from dataclasses import dataclass
import pandas as pd

T = TypeVar('T')


@dataclass(frozen=True)
class Player(Generic[T]):
    id: int
    name: str


@dataclass(frozen=True)
class Team(Generic[T]):
    id: int
    name: str

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Boxscore(Generic[T]):
    id: int
    boxscore: pd.DataFrame


@dataclass(frozen=True)
class Game(Generic[T]):
    id: int
    date: str
    hour: str
    league: str
    season: str
    local_team: Team
    away_team: Team
    local_score: int
    away_score: int
    main_referee: Player
    aux_referee: Player
    local_boxscore: Boxscore
    away_boxscore: Boxscore


@dataclass(frozen=True)
class League(Generic[T]):
    id: int
    name: str
    season: str
    teams: List[Team]
    games: List[Game]

    def __str__(self):
        return f'{self.name} - {self.season}'

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
        if team in {game.local_team, game.away_team}:
            matching_games.append(game)
    return matching_games
