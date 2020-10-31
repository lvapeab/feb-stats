# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import feb_stats_pb2 as feb__stats__pb2


class FebStatsServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetFebStats = channel.unary_unary(
            "/feb_stats.FebStatsService/GetFebStats",
            request_serializer=feb__stats__pb2.GetFebStatsRequest.SerializeToString,
            response_deserializer=feb__stats__pb2.GetFebStatsResponse.FromString,
        )


class FebStatsServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetFebStats(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_FebStatsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "GetFebStats": grpc.unary_unary_rpc_method_handler(
            servicer.GetFebStats,
            request_deserializer=feb__stats__pb2.GetFebStatsRequest.FromString,
            response_serializer=feb__stats__pb2.GetFebStatsResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "feb_stats.FebStatsService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class FebStatsService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetFebStats(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/feb_stats.FebStatsService/GetFebStats",
            feb__stats__pb2.GetFebStatsRequest.SerializeToString,
            feb__stats__pb2.GetFebStatsResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
