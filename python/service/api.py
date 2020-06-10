from google.protobuf import any_pb2
from grpc import ServicerContext
from grpc_status import rpc_status
from google.rpc import code_pb2, status_pb2, error_details_pb2
from opencensus.trace.execution_context import get_opencensus_tracer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc
from typing import Optional


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

    @staticmethod
    def _create_missing_tenant() -> status_pb2.Status:
        detail = any_pb2.Any()
        detail.Pack(
            error_details_pb2.BadRequest(
                violations=[error_details_pb2.BadRequest.FIELD_VIOLATION(
                    field='tenant',
                    description="Tenant must provided via request metadata"
                )]))

        return status_pb2.Status(
            code=code_pb2.INVALID_ARGUMENT,
            message='Field not found',
            details=[detail])

    @staticmethod
    def _get_tentant(context: ServicerContext) -> Optional[str]:
        tenant = context.invocation_metadata()
        tenant = list(filter(lambda x: x[0] == 'tenant', tenant))
        if tenant:
            return tenant[0][1]
        return None

    def GetFebStats(self, request, context):
        with get_opencensus_tracer().span(name='GetFebStats') as span:
            boxscores = request.boxscores
            tenant = self._get_tentant(context)

            if not boxscores:
                rich_status = self._create_missing_parameter_error_status('path')
                context.abort_with_status(rpc_status.to_status(rich_status))

            result = self.league_handler.export_boxscores(boxscores)
            response = feb_stats_pb2.GetFebStatsResponse()

            response.sheet = result
            span.add_annotation('League',
                                sheet=str(result),
                                )

            return response
