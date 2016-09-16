from datetime import datetime

from django.test import TestCase

from events.helpers import add_repeat


class AddRepeatTests(TestCase):

    def test_when_repeating_by_day_should_increase_date_by_one_day(self):
        date = datetime(2016, 12, 31)

        result = add_repeat(date, 'D')

        self.assertEqual(result, datetime(2017, 1, 1))

    def test_when_repeating_by_week_should_increase_date_by_one_week(self):
        date = datetime(2016, 10, 25)

        result = add_repeat(date, 'W')

        self.assertEqual(result, datetime(2016, 11, 1))

    def test_when_repeating_by_month_should_increase_date_by_one_month(self):
        date = datetime(2016, 10, 25)

        result = add_repeat(date, 'M')

        self.assertEqual(result, datetime(2016, 11, 25))

    def test_when_repeating_by_month_and_day_does_not_exist_in_month_should_set_day_to_nearest_day(self):
        date = datetime(2020, 1, 31)

        result = add_repeat(date, 'M')

        self.assertEqual(result, datetime(2020, 2, 29))
