import os
from datetime import timedelta

import signal
import threading
import timeit
import unittest

from python.service.server import Server

class ServerTestCase(unittest.TestCase):

    def test_timely_shutdown(self):
        server = Server(address='127.0.0.1:0')
        server.start()
        start = timeit.default_timer()
        server.stop()
        server.wait_for_termination()
        delta = timedelta(seconds=timeit.default_timer() - start)
        self.assertLessEqual(delta.total_seconds(), 30.0)

    def test_sigterm_shutdown(self):
        server = Server(address='127.0.0.1:0')
        server.start()
        start = timeit.default_timer()
        pid = os.getpid()
        thread = threading.Thread(target=lambda: os.kill(pid, signal.SIGTERM))
        thread.start()
        server.wait_for_termination()
        delta = timedelta(seconds=timeit.default_timer() - start)
        self.assertLessEqual(delta.total_seconds(), 30.0)

if __name__ == '__main__':
    unittest.main()
