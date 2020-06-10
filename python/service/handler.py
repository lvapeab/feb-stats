from abc import ABC, abstractmethod
from grpc import insecure_channel
from python.feb_stats.transforms import export_boxscores_from_bytes
from typing import  List

class LeagueHandler(ABC):
    @abstractmethod
    def export_boxscores(self,
             input_boxscores: List[bytes]) -> bytes:
        raise NotImplementedError()


class SimpleLeagueHandler(LeagueHandler):
    def __init__(self, address: str):
        self.address = address
        self.channel = insecure_channel(self.address)
        self.stub = export_boxscores_from_bytes

    def export_boxscores(self,
             input_boxscores: List[bytes]) -> bytes:
        return self.stub(input_boxscores)
