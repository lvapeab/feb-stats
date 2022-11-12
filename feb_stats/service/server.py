# -*- coding: utf-8 -*-
import argparse
import logging
import os
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

from feb_stats.service.api import FebStatsServiceServicer
from feb_stats.service.codegen import feb_stats_pb2, feb_stats_pb2_grpc
from feb_stats.service.handler import SimpleLeagueHandler

logger = logging.getLogger(__name__)


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
        "--exporter-port",
        action="store",
        dest="exporter_port",
        default=6831,
        type=int,
    )
    return parser


class Server:
    def __init__(
        self,
        address: str,
    ) -> None:
        executor = futures.ThreadPoolExecutor(
            max_workers=min(32, os.cpu_count() or 1)
        )  # Python 3.8 default
        max_message_length = 100 * 1024 * 1024
        options = [
            ("grpc.max_receive_message_length", max_message_length),
            ("grpc.max_send_message_length", max_message_length),
        ]

        self.server = grpc.server(thread_pool=executor, options=options)
        reflection.enable_server_reflection(SERVICE_NAMES, self.server)

        feb_stats_servicer = FebStatsServiceServicer(
            SimpleLeagueHandler("localhost:9000", options=options)
        )
        # TODO: Add healing
        feb_stats_pb2_grpc.add_FebStatsServiceServicer_to_server(
            feb_stats_servicer, self.server
        )
        self.port = self.server.add_insecure_port(address)
        logger.info(f"Server built. Port: {self.port}")

    def start(self) -> None:
        self.server.start()

    def stop(self, grace: int = 30) -> None:
        self.server.stop(grace)

    def wait_for_termination(self) -> None:
        self.server.wait_for_termination()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    server = Server(
        address=f"[::]:{args.port}",
    )
    server.start()
    server.wait_for_termination()
    server.stop()
