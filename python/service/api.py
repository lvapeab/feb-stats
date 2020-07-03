from opencensus.trace.execution_context import get_opencensus_tracer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc


class FebStatsServiceServicer(feb_stats_pb2_grpc.FebStatsServiceServicer):

    def __init__(self,
                 league_handler: SimpleLeagueHandler):
        self.league_handler = league_handler

    def GetFebStats(self, request, context):
        with get_opencensus_tracer().span(name='GetFebStats') as span:
            boxscores = request.boxscores

            # TODO: Add tenants when distributing the computations
            result = self.league_handler.export_boxscores(boxscores)
            response = feb_stats_pb2.GetFebStatsResponse()

            response.sheet = result
            span.add_annotation('League',
                                sheet=str(result),
                                )

            return response
