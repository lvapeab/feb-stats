import unittest
from feb_stats.parser import parse_str

class ParserTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ParserTestCase, self).__init__(*args, **kwargs)

    def test_parse_str(self):
        test_str = '             Rebotes                            D          O          T '
        desired_test_str = 'Rebotes D O T'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = '\n\t\t\t\t\t\t\n\t\t\t\t\nRebotes\n\t\t\t\t\t\n\t\t\tD\n\t\t\t\t\t\tO\n\t\t\t\t\t\tT\n\t\t\t\t\t\t'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = '                       0                               0                               0           '
        desired_test_str = '0 0 0'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = '\n\t\t\t\t\t\t\n\t\t\t\t\n0\n\t\t\t\t\t\n\t\t\t0\n\t\t\t\t\t\t0\t\t\t\t\t'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)


        test_str = '             Tapones                            Fa          Co          '
        desired_test_str = 'Tapones Fa Co'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)

        test_str = '                       0                               0           '
        desired_test_str = '0 0'
        out_str = parse_str(test_str)
        self.assertEqual(out_str, desired_test_str)



if __name__ == '__main__':
    unittest.main()
