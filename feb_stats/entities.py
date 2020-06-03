from dataclasses import dataclass, field
import os
import pandas as pd
from typing import TypeVar, Generic, List, Optional, Set

from feb_stats.utils import league_to_excel

T = TypeVar('T')


@dataclass(frozen=True)
class Player(Generic[T]):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None


@dataclass(frozen=True)
class Team(Generic[T]):
    id: int
    name: str
    season_stats: Optional[pd.DataFrame] = None

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Boxscore(Generic[T]):
    boxscore: pd.DataFrame
    id: Optional[int] = None


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
    teams: Set[Team]
    games: List[Game]
    aggregated_games: Optional[pd.DataFrame] = None

    def __str__(self):
        return f'{self.name} - {self.season}'

    def export_to_excel(self,
                        dir: Optional[str] = None,
                        filename: Optional[str] = None, ) -> None:
        dir = dir or '.'
        filename = filename or f'{self.name}_{self.season.replace("/", "-")}.xlsx'
        if self.aggregated_games is not None:
            league_to_excel(self,
                            os.path.join(dir, filename),
                            sheet_name=f'{self.name}_{self.season.replace("/", "-")}')
        else:
            raise NotImplementedError('Still unimplemented')


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


def get_team_boxscores(league: League,
                       team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.local_team == team else game.away_boxscore
            for game in get_games_by_team(league, team)]


def get_rival_boxscores(league: League,
                        team: Team) -> List[Boxscore]:
    return [game.local_boxscore if game.local_team != team else game.away_boxscore
            for game in get_games_by_team(league, team)]
