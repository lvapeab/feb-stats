from abc import ABC, abstractmethod

from grpc import insecure_channel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from feb_stats.core.entities import League
from feb_stats.core.saving import league_to_xlsx
from feb_stats.core.transforms import compute_league_aggregates
from feb_stats.parsers.feb_livescore_parser import FEBLivescoreParser


class LeagueHandler(ABC):
    @abstractmethod
    def export_boxscores(self, input_boxscores: list[bytes], color_sheet: bool) -> bytes:
        raise NotImplementedError()


class SimpleLeagueHandler(LeagueHandler):
    def __init__(self, address: str, options: list[tuple[str, int]] | None = None) -> None:
        self.options = options
        self.address = address
        self.channel = insecure_channel(self.address, options=self.options)
        self.league: League | None = None

    def parse_boxscores(self, input_boxscores: list[bytes]) -> None:
        league = FEBLivescoreParser.parse_boxscores(input_boxscores, FEBLivescoreParser.read_link_bytes)
        self.league = compute_league_aggregates(league)
        return None

    def export_boxscores(self, input_boxscores: list[bytes], color_sheet: bool) -> bytes:
        self.parse_boxscores(input_boxscores)
        assert self.league is not None
        return league_to_xlsx(self.league, export_colors=color_sheet)

    def clean_league(self) -> None:
        self.league = None
