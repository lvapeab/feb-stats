import unittest
from python.service.handler import SimpleLeagueHandler


class DummyBinaryDetectorHandler(SimpleLeagueHandler):
    # TODO
    pass


class ContextStub:
    def invocation_metadata(self):
        return [('tenant', 'test')]


class FebStatsServiceServicerTest(unittest.TestCase):

    def test_GetFebStats(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
