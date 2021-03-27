import glob
import unittest

from python.service.api import FebStatsServiceServicer, ContextStub
from python.service.codegen.feb_stats_pb2 import GetFebStatsRequest
from python.service.handler import SimpleLeagueHandler


class FebStatsServiceServicerTest(unittest.TestCase):
    def test_GetFebStats(self) -> None:
        input_files = glob.glob("test_data/*livescore*html")
        boxscores = []
        for file in input_files:
            with open(file, mode="rb") as f:
                boxscores.append(f.read())
        request = GetFebStatsRequest(boxscores=boxscores, )
        service = FebStatsServiceServicer(SimpleLeagueHandler(address="8008"))
        result = service.GetFebStats(request, ContextStub())
        self.assertTrue(result.sheet)


if __name__ == "__main__":
    unittest.main()
