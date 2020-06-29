import os
from datetime import timedelta

import signal
import threading
import timeit
import unittest

from grpc import insecure_channel
from python.service.server import Server


class ServerTestCase(unittest.TestCase):
    def _send_health_check(self, port: int) -> None:
        with insecure_channel(f'127.0.0.1:{port}') as channel:
            pass
            """
            health_stub = health_pb2_grpc.HealthStub(channel)
            response = health_stub.Check(health_pb2.HealthCheckRequest(service=''))  # overall health
            # just ensure a valid response, doesn't matter if we can make a real request
            self.assertIn(
                response.status,
                {health_pb2.HealthCheckResponse.NOT_SERVING,
                 health_pb2.HealthCheckResponse.SERVING,
                 })
            """

    def test_timely_shutdown(self):
        server = Server(address='127.0.0.1:0')
        server.start()
        self._send_health_check(server.port)
        start = timeit.default_timer()
        server.stop()
        server.wait_for_termination()
        delta = timedelta(seconds=timeit.default_timer() - start)
        self.assertLessEqual(delta.total_seconds(), 10.0)

    def test_sigterm_shutdown(self):
        server = Server(address='127.0.0.1:0')
        server.start()
        self._send_health_check(server.port)
        start = timeit.default_timer()
        pid = os.getpid()
        thread = threading.Thread(target=lambda: os.kill(pid, signal.SIGTERM))
        thread.start()
        server.wait_for_termination()
        delta = timedelta(seconds=timeit.default_timer() - start)
        self.assertLessEqual(delta.total_seconds(), 10.0)


if __name__ == '__main__':
    unittest.main()
