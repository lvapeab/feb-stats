import unittest
from typing import Any

from feb_stats.service.handler import SimpleLeagueHandler


class BinaryDetectorHandlerTest(unittest.TestCase):
    def __init__(self,
                 *args: Any,
                 **kwargs: Any) -> None:
        super(BinaryDetectorHandlerTest, self).__init__(*args, **kwargs)
        self.handler = SimpleLeagueHandler(address="8008")

    def test_export_boxscores(self) -> None:
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
