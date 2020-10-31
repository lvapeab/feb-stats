from abc import ABC, abstractmethod
from grpc import insecure_channel
from python.feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser
from python.feb_stats.entities import League
from python.feb_stats.transforms import compute_league_aggregates
from python.feb_stats.saving import league_to_xlsx
from typing import List, Tuple, Optional


class LeagueHandler(ABC):
    @abstractmethod
    def export_boxscores(self, input_boxscores: List[bytes]) -> bytes:
        raise NotImplementedError()


class SimpleLeagueHandler(LeagueHandler):
    def __init__(self, address: str, options: Optional[List[Tuple]] = None):
        self.options = options
        self.address = address
        self.channel = insecure_channel(self.address, options=self.options)
        self.league: League = None

    def parse_boxscores(self, input_boxscores: List[bytes]) -> None:
        league = FEBLivescoreParser().parse_boxscores(input_boxscores)
        self.league = compute_league_aggregates(league)
        return None

    def export_boxscores(self, input_boxscores: Optional[List[bytes]]) -> bytes:
        if not input_boxscores or self.league is None:
            self.parse_boxscores(input_boxscores)
        return league_to_xlsx(self.league)

    def clean_league(self) -> None:
        self.league = None
