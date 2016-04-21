from datetime import date, time
from django.test import TestCase
from rest_framework import serializers
from events.serializers import EventsSerializer

class EventsSerializerTests(TestCase):
    serializer = EventsSerializer()

    def test_when_event_is_repeating_and_has_no_repetition_end_date_should_raise_error(self):
        event = {
            'title': 'Foo',
            'start_date': date(2016, 1, 1),
            'start_time': time(1, 0, 0),
            'end_date': date(2016, 1, 1),
            'end_time': time(2, 0, 0),
            'is_repeat': True,
            'repetition': None,
            'ends': date(2016, 2, 1)
        }

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate(event)

    def test_when_event_start_date_is_after_end_date_should_raise_error(self):
        event = {
            'title': 'Foo',
            'start_date': date(2016, 1, 2),
            'start_time': time(1, 0, 0),
            'end_date': date(2016, 1, 1),
            'end_time': time(2, 0, 0),
            'is_repeat': False,
            'repetition': None,
            'ends': None
        }

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate(event)

    def test_when_event_start_date_equals_end_date_and_start_time_is_after_end_time_should_raise_error(self):
        event = {
            'title': 'Foo',
            'start_date': date(2016, 1, 1),
            'start_time': time(3, 0, 0),
            'end_date': date(2016, 1, 1),
            'end_time': time(2, 0, 0),
            'is_repeat': False,
            'repetition': None,
            'ends': None
        }

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate(event)

    def test_when_event_repeats_and_ends_is_after_start_date_should_raise_error(self):
        event = {
            'title': 'Foo',
            'start_date': date(2016, 3, 1),
            'start_time': time(1, 0, 0),
            'end_date': date(2016, 3, 1),
            'end_time': time(2, 0, 0),
            'is_repeat': True,
            'repetition': 'Monthly',
            'ends': date(2016, 2, 1)
        }

        with self.assertRaises(serializers.ValidationError):
            self.serializer.validate(event)