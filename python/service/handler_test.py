import unittest
from python.service.handler import SimpleLeagueHandler


class BinaryDetectorHandlerTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(BinaryDetectorHandlerTest, self).__init__(*args, **kwargs)
        self.handler = SimpleLeagueHandler(address='8008')



    def test_export_boxscores(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
