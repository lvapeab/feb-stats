import glob
import unittest
from pathlib import Path
from feb_stats.service.api import ContextStub, FebStatsServiceServicer
from feb_stats.service.codegen.feb_stats_pb2 import GetFebStatsRequest
from feb_stats.service.handler import SimpleLeagueHandler


class FebStatsServiceServicerTest(unittest.TestCase):
    def test_GetFebStats(self) -> None:
        test_dir = Path(__file__).parent.parent.parent
        input_files = glob.glob(str(test_dir / "data/*livescore*html"))
        boxscores = []
        for file in input_files:
            with open(file, mode="rb") as f:
                boxscores.append(f.read())
        request = GetFebStatsRequest(boxscores=boxscores)
        service = FebStatsServiceServicer(SimpleLeagueHandler(address="8008"))
        result = service.GetFebStats(request, ContextStub())
        self.assertTrue(result.sheet)

        request_with_color = GetFebStatsRequest(boxscores=boxscores, color_sheet=True)
        result_with_color = service.GetFebStats(request_with_color, ContextStub())
        self.assertTrue(result_with_color.sheet)


if __name__ == "__main__":
    unittest.main()
