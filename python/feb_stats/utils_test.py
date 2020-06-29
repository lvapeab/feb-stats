import unittest
import pandas as pd
from python.feb_stats.utils import timedelta_to_minutes, timedelta_to_str, get_sorted_list_of_columns, \
    get_averageable_numerical_columns, response_to_excel


class UtilsTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(UtilsTestCase, self).__init__(*args, **kwargs)

    def test_timedelta_to_str(self):
        day_timedelta = pd.Timedelta(days=1)
        self.assertEqual('1440:00', timedelta_to_str(day_timedelta))

        hour_timedelta = pd.Timedelta(hours=1)
        self.assertEqual('060:00', timedelta_to_str(hour_timedelta))

        minutes_timedelta = pd.Timedelta(minutes=1)
        self.assertEqual('001:00', timedelta_to_str(minutes_timedelta))

        seconds_timedelta = pd.Timedelta(seconds=1)
        self.assertEqual('000:01', timedelta_to_str(seconds_timedelta))

    def test_timedelta_to_minutes(self):
        day_timedelta = pd.Timedelta(days=1)
        self.assertEqual(1440., timedelta_to_minutes(day_timedelta))

        hour_timedelta = pd.Timedelta(hours=1)
        self.assertEqual(60., timedelta_to_minutes(hour_timedelta))

        minutes_timedelta = pd.Timedelta(minutes=1)
        self.assertEqual(1., timedelta_to_minutes(minutes_timedelta))

        seconds_timedelta = pd.Timedelta(seconds=1)
        self.assertAlmostEqual(0.016666666, timedelta_to_minutes(seconds_timedelta))

    def test_get_sorted_list_of_columns(self):
        sorted_list = get_sorted_list_of_columns(individual_columns=False)
        self.assertEqual(len(sorted_list), 34)
        sorted_list = get_sorted_list_of_columns(individual_columns=True)
        self.assertEqual(len(sorted_list), 44)

    def test_get_averageable_numerical_columns(self):
        averageable_list = get_averageable_numerical_columns(individual_columns=False)
        self.assertEqual(len(averageable_list), 25)
        averageable_list = get_averageable_numerical_columns(individual_columns=True)
        self.assertEqual(len(averageable_list), 24)

    def test_response_to_excel(self):
        pass


if __name__ == '__main__':
    unittest.main()
