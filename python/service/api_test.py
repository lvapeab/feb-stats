import glob
from python.service.api import FebStatsServiceServicer
from python.service.handler import LeagueHandler, SimpleLeagueHandler
from python.service.codegen.feb_stats_pb2 import GetFebStatsRequest
import unittest


class ContextStub:
    def invocation_metadata(self):
        return [('tenant', 'test')]


class FebStatsServiceServicerTest(unittest.TestCase):

    def test_GetFebStats(self):
        input_files = glob.iglob('test_data/*html')
        boxscores = []
        for file in input_files:
            with open(file, mode='rb') as f:
                boxscores.append(f.read())
        request = GetFebStatsRequest(
            boxscores=boxscores,
        )
        service = FebStatsServiceServicer(SimpleLeagueHandler(address='8008'))
        result = service.GetFebStats(request, ContextStub())
        self.assertTrue(result.sheet)


if __name__ == "__main__":
    unittest.main()
