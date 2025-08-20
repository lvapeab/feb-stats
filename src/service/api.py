from src.service.codegen import feb_stats_pb2_grpc
from src.service.codegen.feb_stats_pb2 import (
    GetFebStatsRequest,
    GetFebStatsResponse,
)
from src.service.handler import SimpleLeagueHandler


class ContextStub:
    def invocation_metadata(self) -> list[tuple[str, str]]:
        return [("tenant", "test")]


class FebStatsServiceServicer(feb_stats_pb2_grpc.FebStatsServiceServicer):
    def __init__(self, league_handler: SimpleLeagueHandler):
        self.league_handler = league_handler

    def GetFebStats(self, request: GetFebStatsRequest, context: ContextStub | None) -> GetFebStatsResponse:
        boxscores: list[bytes] = request.boxscores  # type:ignore
        color_sheet: bool = request.color_sheet
        # TODO: Add tenants when distributing the computations
        result = self.league_handler.export_boxscores(boxscores, color_sheet)
        response = GetFebStatsResponse()

        response.sheet = result
        # TODO(alvaro)
        # response.teams.extend([str(t) for t in self.league_handler.league.teams])
        self.league_handler.clean_league()
        return response
