from datetime import date, timedelta

from django.test import TestCase

from events.helpers import get_repeated_events, repeating_date_generator
from events.tests.factories import EventFactory


class GetRepeatedEventsTests(TestCase):

    def test_should_return_event_instances_in_date_range(self):
        today = date.today()
        title = 'Foo'
        repeated_event_properties = {
            'title': title,
            'start_date': today,
            'end_date': today,
            'is_repeat': True,
            'repetition': 'D',
            'ends': today + timedelta(days=20)
        }
        event = EventFactory.create(**repeated_event_properties)

        events = get_repeated_events([event], today, today + timedelta(days=2))

        self.assertEqual(len(events), 2)
        for day in events:
            self.assertEquals(day.title, repeated_event_properties['title'])

    def test_when_event_repetition_ends_before_end_date_range_should_return_event_instances_before_repetition_end_date(self):
        today = date.today()
        title = 'Foo'
        repeated_event_properties = {
            'title': title,
            'start_date': today,
            'end_date': today,
            'is_repeat': True,
            'repetition': 'D',
            'ends': today + timedelta(days=2)
        }
        event = EventFactory.create(**repeated_event_properties)

        events = get_repeated_events([event], today, today + timedelta(days=20))

        self.assertEqual(len(events), 2)
        for day in events:
            self.assertEquals(day.title, repeated_event_properties['title'])


class RepeatingDateGeneratorTests(TestCase):

    def test_when_repeating_by_day_should_increase_date_by_one_day(self):
        start_date = date(2016, 12, 31)
        gen = repeating_date_generator(start_date, 'D')

        result = gen.next()
        self.assertEqual(result, date(2017, 1, 1))

        result = gen.next()
        self.assertEqual(result, date(2017, 1, 2))

    def test_when_repeating_by_week_should_increase_date_by_one_week(self):
        start_date = date(2016, 10, 25)
        gen = repeating_date_generator(start_date, 'W')

        result = gen.next()
        self.assertEqual(result, date(2016, 11, 1))

        result = gen.next()
        self.assertEqual(result, date(2016, 11, 8))

    def test_when_repeating_by_month_should_increase_date_by_one_month(self):
        start_date = date(2016, 11, 25)
        gen = repeating_date_generator(start_date, 'M')

        result = gen.next()
        self.assertEqual(result, date(2016, 12, 25))

        result = gen.next()
        self.assertEqual(result, date(2017, 1, 25))

    def test_when_repeating_by_month_and_day_does_not_exist_in_month_should_set_day_to_nearest_day(self):
        start_date = date(2020, 1, 31)
        gen = repeating_date_generator(start_date, 'M')

        result = gen.next()
        self.assertEqual(result, date(2020, 2, 29))

        result = gen.next()
        self.assertEqual(result, date(2020, 3, 31))