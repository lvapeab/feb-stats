from typing import List, Tuple, Optional

from feb_stats.service.codegen import feb_stats_pb2_grpc
from feb_stats.service.codegen.feb_stats_pb2 import GetFebStatsResponse, GetFebStatsRequest
from feb_stats.service.handler import SimpleLeagueHandler


class ContextStub:
    def invocation_metadata(self) -> List[Tuple[str, str]]:
        return [("tenant", "test")]


class FebStatsServiceServicer(feb_stats_pb2_grpc.FebStatsServiceServicer):
    def __init__(self, league_handler: SimpleLeagueHandler):
        self.league_handler = league_handler

    def GetFebStats(self,
                    request: GetFebStatsRequest,
                    context: Optional[ContextStub]) -> GetFebStatsResponse:
        boxscores: List[bytes] = request.boxscores  # type:ignore
        # TODO: Add tenants when distributing the computations
        result = self.league_handler.export_boxscores(boxscores)
        response = GetFebStatsResponse()

        response.sheet = result
        # TODO(alvaro)
        # response.teams.extend([str(t) for t in self.league_handler.league.teams])
        self.league_handler.clean_league()
        return response
