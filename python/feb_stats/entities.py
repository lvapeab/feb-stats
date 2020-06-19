from dataclasses import dataclass
import pandas as pd
from typing import TypeVar, Generic, List, Optional

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
    teams: List[Team]
    games: List[Game]
    aggregated_games: Optional[pd.DataFrame] = None

    def __str__(self):
        return f'{self.name} - {self.season}'