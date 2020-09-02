# -*- coding: utf-8 -*-
import argparse
import grpc
import os
import signal
from concurrent import futures
from grpc_reflection.v1alpha import reflection

from opencensus.ext.prometheus import stats_exporter as prometheus

from opencensus.ext.grpc.server_interceptor import OpenCensusServerInterceptor
from opencensus.ext.jaeger.trace_exporter import JaegerExporter
from opencensus.trace.samplers import AlwaysOnSampler

from types import FrameType
from typing import Optional
from datetime import timedelta

from python.service.api import FebStatsServiceServicer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc

SERVICE_NAMES = [
    reflection.SERVICE_NAME,
    *[
        service.full_name
        for service in feb_stats_pb2.DESCRIPTOR.services_by_name.values()
    ],
]


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("FEB stats API Service")

    parser.add_argument("--port", action="store", dest="port", default=50001, type=str)
    parser.add_argument(
        "--exporter-host-name",
        action="store",
        dest="exporter_host_name",
        default="jaeger",
        type=str,
    )
    parser.add_argument(
        "--exporter-port", action="store", dest="exporter_port", default=6831, type=int,
    )
    return parser


class Server:
    def __init__(
        self,
        address: str,
        exporter_host_name: Optional[str] = "localhost",
        exporter_port: Optional[int] = 6831,
    ) -> None:
        exporter = JaegerExporter(
            service_name="stats-analyzer",
            agent_host_name=exporter_host_name,  # TODO: Eventually switch to another service (e.g. istio)
            agent_port=exporter_port,  # <- accept jaeger.thrift over compact thrift protocol
        )
        tracer_interceptor = OpenCensusServerInterceptor(
            AlwaysOnSampler(), exporter=exporter
        )
        executor = futures.ThreadPoolExecutor(
            max_workers=min(32, os.cpu_count() + 4)
        )  # Python 3.8 default
        max_message_length = 100 * 1024 * 1024
        options = [
            ("grpc.max_receive_message_length", max_message_length),
            ("grpc.max_send_message_length", max_message_length),
        ]

        self.server = grpc.server(
            thread_pool=executor, interceptors=(tracer_interceptor,), options=options
        )
        reflection.enable_server_reflection(SERVICE_NAMES, self.server)

        feb_stats_servicer = FebStatsServiceServicer(
            SimpleLeagueHandler("localhost:9000", options=options)
        )
        # TODO: Add healing
        feb_stats_pb2_grpc.add_FebStatsServiceServicer_to_server(
            feb_stats_servicer, self.server
        )
        signal.signal(signalnum=signal.Signals.SIGTERM, handler=self._sigterm_handler)
        self.port = self.server.add_insecure_port(address)
        print(f"Server built. Port: {self.port}")

    def _sigterm_handler(self, _signum: signal.Signals, _frame: FrameType) -> None:
        self.server.stop(grace=timedelta(seconds=30))

    def start(self) -> None:
        self.server.start()

    def stop(self, grace=None) -> None:
        self.server.stop(grace)

    def wait_for_termination(self) -> None:
        self.server.wait_for_termination()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    server = Server(
        address=f"[::]:{args.port}",
        exporter_host_name=args.exporter_host_name,
        exporter_port=args.exporter_port,
    )
    server.start()
    server.wait_for_termination()
    server.stop()
