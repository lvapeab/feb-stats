from google.protobuf import any_pb2
from google.rpc import code_pb2, status_pb2, error_details_pb2
from opencensus.trace.execution_context import get_opencensus_tracer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc


class FebStatsServiceServicer(feb_stats_pb2_grpc.FebStatsServiceServicer):

    def __init__(self,
                 league_handler: SimpleLeagueHandler):
        self.league_handler = league_handler

    @staticmethod
    def _create_missing_parameter_error_status(field_name: str) -> status_pb2.Status:
        detail = any_pb2.Any()
        detail.Pack(
            error_details_pb2.BadRequest(
                violations=[error_details_pb2.BadRequest.FIELD_VIOLATION(
                    field=field_name,
                    description='Field must be specified'
                )]))

        return status_pb2.Status(
            code=code_pb2.INVALID_ARGUMENT,
            message='Field not found',
            details=[detail])


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
