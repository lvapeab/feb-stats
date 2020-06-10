# -*- coding: utf-8 -*-
import sys
import argparse
import grpc
import os
import signal
import pathlib
from concurrent import futures
from grpc_reflection.v1alpha import reflection

from opencensus.common.transports.async_ import AsyncTransport
from opencensus.ext.grpc.server_interceptor import OpenCensusServerInterceptor
from opencensus.ext.jaeger.trace_exporter import JaegerExporter
from opencensus.ext.stackdriver.trace_exporter import StackdriverExporter
from opencensus.trace.samplers import AlwaysOnSampler

from types import FrameType
from datetime import timedelta

from python.service.api import FebStatsServiceServicer
from python.service.handler import SimpleLeagueHandler
from python.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc

SERVICE_NAMES = [
    reflection.SERVICE_NAME,
    *[service.full_name for service in feb_stats_pb2.DESCRIPTOR.services_by_name.values()],
]

parser = argparse.ArgumentParser('FEB stats API Service')
parser.add_argument('-local', action='store_true', dest='local')


class Server:
    def __init__(self,
                 local: bool,
                 address: str) -> None:
        if local:
            exporter = JaegerExporter(service_name='pdf_filler',
                                      agent_host_name='tracing.istio-system',
                                      agent_port=80, )
        else:
            exporter = StackdriverExporter(transport=AsyncTransport)

        tracer_interceptor = OpenCensusServerInterceptor(AlwaysOnSampler(), exporter=exporter)
        executor = futures.ThreadPoolExecutor(max_workers=min(32, os.cpu_count() + 4))  # Python 3.8 default
        self.server = grpc.server(thread_pool=executor, interceptors=(tracer_interceptor,))
        reflection.enable_server_reflection(SERVICE_NAMES, self.server)

        feb_stats_servicer = FebStatsServiceServicer(
            SimpleLeagueHandler('localhost:9000')
        )
        # TODO: Add healing
        feb_stats_pb2_grpc.add_FebStatsServiceServicer_to_server(feb_stats_servicer, self.server)
        signal.signal(signalnum=signal.Signals.SIGTERM, handler=self._sigterm_handler)
        self.port = self.server.add_insecure_port(address)
        print("Server built. Port:", self.port)

    def _sigterm_handler(self, _signum: signal.Signals, _frame: FrameType) -> None:
        self.server.stop(grace=timedelta(seconds=30))

    def start(self) -> None:
        self.server.start()

    def stop(self, grace=None) -> None:
        self.server.stop(grace)

    def wait_for_termination(self) -> None:
        self.server.wait_for_termination()


if __name__ == '__main__':
    args = parser.parse_args()
    server = Server(
        local=args.local,
        address='[::]:50001')
    server.start()
    server.wait_for_termination()
    server.stop()
