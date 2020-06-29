from abc import ABC, abstractmethod
from grpc import insecure_channel
from python.feb_stats.parsers.feb_parser import FEBParser
from python.feb_stats.transforms import compute_league_aggregates
from python.feb_stats.entities_ops import league_to_excel
from typing import List, Tuple, Optional


class LeagueHandler(ABC):
    @abstractmethod
    def export_boxscores(self,
                         input_boxscores: List[bytes]) -> bytes:
        raise NotImplementedError()


class SimpleLeagueHandler(LeagueHandler):
    def __init__(self,
                 address: str,
                 options: Optional[List[Tuple]] = None
                 ):
        self.options = options
        self.address = address
        self.channel = insecure_channel(self.address,
                                        options=self.options)

    def export_boxscores(self,
                         input_boxscores: List[bytes]) -> bytes:
        league = FEBParser().parse_boxscores(input_boxscores)
        new_league = compute_league_aggregates(league)
        return league_to_excel(new_league)

