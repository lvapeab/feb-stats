from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from grpc import insecure_channel

from feb_stats.core.entities import League
from feb_stats.core.saving import league_to_xlsx
from feb_stats.core.transforms import compute_league_aggregates
from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser


class LeagueHandler(ABC):
    @abstractmethod
    def export_boxscores(
        self, input_boxscores: List[bytes], color_sheet: bool
    ) -> bytes:
        raise NotImplementedError()


class SimpleLeagueHandler(LeagueHandler):
    def __init__(
        self, address: str, options: Optional[List[Tuple[str, int]]] = None
    ) -> None:
        self.options = options
        self.address = address
        self.channel = insecure_channel(self.address, options=self.options)
        self.league: Optional[League] = None

    def parse_boxscores(self, input_boxscores: List[bytes]) -> None:
        league = FEBLivescoreParser().parse_boxscores(input_boxscores)
        self.league = compute_league_aggregates(league)
        return None

    def export_boxscores(
        self, input_boxscores: List[bytes], color_sheet: bool
    ) -> bytes:
        self.parse_boxscores(input_boxscores)
        assert self.league is not None
        return league_to_xlsx(self.league, export_colors=color_sheet)

    def clean_league(self) -> None:
        self.league = None
