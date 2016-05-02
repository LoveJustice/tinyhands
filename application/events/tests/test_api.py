import datetime
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.tests.factories import ViewUserFactory
from events.tests.factories import EventFactory

class RestApiTestCase(APITestCase):

    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class GetEventAPITests(RestApiTestCase):

    def test_when_not_logged_in_should_return_403_error(self):
        url = reverse('Event', args=[101])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_logged_in_and_event_does_not_exist_should_return_404(self):
        url = reverse('Event', args=[101])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_when_user_logged_in_and_event_exists_should_return_event(self):
        event = EventFactory.create()
        url = reverse('Event', args=[event.id])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], event.id)
        self.assertEqual(response.data['title'], event.title)
        self.assertEqual(response.data['location'], event.location)
        self.assertEqual(response.data['start_date'], str(event.start_date))
        self.assertEqual(response.data['start_time'], str(event.start_time))
        self.assertEqual(response.data['end_date'], str(event.end_date))
        self.assertEqual(response.data['end_time'], str(event.end_time))
        self.assertEqual(response.data['description'], event.description)
        self.assertEqual(response.data['is_repeat'], event.is_repeat)
        self.assertEqual(response.data['repetition'], event.repetition)
        self.assertEqual(response.data['ends'], str(event.ends))


class CreateEventAPITests(RestApiTestCase):
    newEvent = {
        'title': 'Foo',
        'location': '',
        'start_date': datetime.date(2016, 2, 2),
        'start_time': datetime.time(3, 0, 0),
        'end_date': datetime.date(2016, 2, 2),
        'end_time': datetime.time(4, 0, 0),
        'description': 'foo',
        'is_repeat': False,
        'repetition': '',
        'ends': None
    }

    def test_when_not_logged_in_should_return_403_error(self):
        url = reverse('EventList')

        response = self.client.post(url, self.newEvent)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_when_user_logged_in_and_valid_event_should_return_event(self):
        url = reverse('EventList')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.post(url, self.newEvent)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['title'], self.newEvent['title'],)
        self.assertEqual(response.data['location'], self.newEvent['location'])
        self.assertEqual(response.data['start_date'], str(self.newEvent['start_date']))
        self.assertEqual(response.data['start_time'], str(self.newEvent['start_time']))
        self.assertEqual(response.data['end_date'], str(self.newEvent['end_date']))
        self.assertEqual(response.data['end_time'], str(self.newEvent['end_time']))
        self.assertEqual(response.data['description'], self.newEvent['description'])
        self.assertEqual(response.data['is_repeat'], self.newEvent['is_repeat'])
        self.assertEqual(response.data['repetition'], self.newEvent['repetition'])
        self.assertEqual(response.data['ends'], self.newEvent['ends'])


class UpdateEventAPITests(RestApiTestCase):

    def test_when_not_logged_in_should_return_403_error(self):
        event = EventFactory.create()
        url = reverse('Event', args=[event.id])

        updatedEvent = {
            'title': "My updated title",
            'location': event.location,
            'start_date': event.start_date,
            'start_time': event.start_time,
            'end_date': event.end_date,
            'end_time': event.end_time,
            'description': event.description,
            'is_repeat': event.is_repeat,
            'repetition': event.repetition,
            'ends': event.ends
        }

        response = self.client.put(url, updatedEvent)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_logged_in_and_valid_event_data_should_return_200(self):
        event = EventFactory.create()
        url = reverse('update_event', args=[event.id])
        user = ViewUserFactory.create()
        self.login(user)

        updatedEvent = {
            'id': event.id,
            'title': "My updated title",
            'location': event.location,
            'start_date': event.start_date,
            'start_time': event.start_time,
            'end_date': event.end_date,
            'end_time': event.end_time,
            'description': event.description,
            'is_repeat': event.is_repeat,
            'repetition': event.repetition,
            'ends': event.ends
        }

        response = self.client.put(url, updatedEvent)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DestroyEventAPITests(RestApiTestCase):

    def test_when_not_logged_in_should_return_403_error(self):
        event = EventFactory.create()
        url = reverse('Event', args=[event.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_logged_in_and_invalid_event_data_should_return_404_error(self):
        url = reverse('Event', args=[101])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_when_user_logged_in_and_valid_event_data_should_return_204(self):
        event = EventFactory.create()
        url = reverse('Event', args=[event.id])
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AllEventAPITests(RestApiTestCase):
    newEvent = {
        'title': 'Foo',
        'location': '',
        'start_date': datetime.date(2016, 2, 2),
        'start_time': datetime.time(3, 0, 0),
        'end_date': datetime.date(2016, 2, 2),
        'end_time': datetime.time(4, 0, 0),
        'description': 'foo',
        'is_repeat': False,
        'repetition': '',
        'ends': None
    }

    def test_when_not_logged_in_should_return_403_error(self):
        url = '/api/event/all/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_user_logged_in_should_return_all_event(self):
        event = EventFactory.create()
        url = '/api/event/all/'
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.post(reverse('EventList'), self.newEvent)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)
        self.assertEqual(response.data[0]['id'], event.id)
        self.assertEqual(response.data[0]['title'], event.title)
        self.assertEqual(response.data[0]['location'], event.location)
        self.assertEqual(response.data[0]['start_date'], str(event.start_date))
        self.assertEqual(response.data[0]['start_time'], str(event.start_time))
        self.assertEqual(response.data[0]['end_date'], str(event.end_date))
        self.assertEqual(response.data[0]['end_time'], str(event.end_time))
        self.assertEqual(response.data[0]['description'], event.description)
        self.assertEqual(response.data[0]['is_repeat'], event.is_repeat)
        self.assertEqual(response.data[0]['repetition'], event.repetition)
        self.assertEqual(response.data[0]['ends'], str(event.ends))
        self.assertIsNotNone(response.data[1]['id'])
        self.assertEqual(response.data[1]['title'], self.newEvent['title'],)
        self.assertEqual(response.data[1]['location'], self.newEvent['location'])
        self.assertEqual(response.data[1]['start_date'], str(self.newEvent['start_date']))
        self.assertEqual(response.data[1]['start_time'], str(self.newEvent['start_time']))
        self.assertEqual(response.data[1]['end_date'], str(self.newEvent['end_date']))
        self.assertEqual(response.data[1]['end_time'], str(self.newEvent['end_time']))
        self.assertEqual(response.data[1]['description'], self.newEvent['description'])
        self.assertEqual(response.data[1]['is_repeat'], self.newEvent['is_repeat'])
        self.assertEqual(response.data[1]['repetition'], self.newEvent['repetition'])
        self.assertEqual(response.data[1]['ends'], self.newEvent['ends'])


class CalendarFeedAPITests(RestApiTestCase):

    def test_when_not_logged_in_should_return_403_error(self):
        url = reverse('EventCalendarFeed')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_when_no_start_and_end_date_in_query_should_return_400_error(self):
        url = reverse('EventCalendarFeed')
        user = ViewUserFactory.create()
        self.login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'Date does not match format YYYY-MM-DD')

    def test_when_start_date_is_later_than_end_date_should_return_400_error(self):
        url = reverse('EventCalendarFeed')
        user = ViewUserFactory.create()
        start_date = datetime.date.today()
        end_date = start_date - datetime.timedelta(days=7)
        self.login(user)

        response = self.client.get(url, {'start': start_date, 'end': end_date})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'Start date is later than end date')

    def test_when_dates_are_valid_should_return_events_in_date_range(self):
        url = reverse('EventCalendarFeed')
        user = ViewUserFactory.create()
        event = EventFactory.create(is_repeat=False)
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=2)
        outsideEvent = EventFactory.create(start_date=end_date+datetime.timedelta(days=1), end_date=end_date+datetime.timedelta(days=2))
        self.login(user)

        response = self.client.get(url, {'start': start_date, 'end': end_date})

        self.assertEquals(len(response.data), 1)
        self.assertEquals(response.data[0]['title'], event.title)
        self.assertEquals(response.data[0]['location'], event.location)

    def test_when_event_is_repeated_should_return_multiple_events(self):
        url = reverse('EventCalendarFeed')
        user = ViewUserFactory.create()
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=2)
        repeatedEventProperties = {
            'start_date': start_date,
            'end_date': end_date,
            'is_repeat': True,
            'repetition': 'D',
            'ends': end_date + datetime.timedelta(days=4)
        }
        repeatedEvent = EventFactory.create(**repeatedEventProperties)
        self.login(user)

        response = self.client.get(url, {'start': start_date, 'end': end_date})

        self.assertEquals(len(response.data), 2)
        self.assertEquals(response.data[0]['title'], repeatedEvent.title)
        self.assertEquals(response.data[0]['location'], repeatedEvent.location)
        self.assertEquals(response.data[1]['title'], repeatedEvent.title)
        self.assertEquals(response.data[1]['location'], repeatedEvent.location)


class DashboardFeedAPITests(RestApiTestCase):

    def test_when_not_logged_in_should_return_403_error(self):
        url = reverse('EventDashboardFeed')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_return_events_that_occur_within_one_week(self):
        url = reverse('EventDashboardFeed')
        user = ViewUserFactory.create()
        today = datetime.date.today()
        event = EventFactory.create(is_repeat=False)
        event2 = EventFactory.create(start_date=today+datetime.timedelta(days=1), is_repeat=False)
        outsideEvent = EventFactory.create(start_date=today+datetime.timedelta(days=8))
        self.login(user)

        response = self.client.get(url)

        for idx, day in enumerate(response.data):
            if idx == 0:
                self.assertEquals(day[1]['title'], event.title)
                self.assertEquals(day[1]['location'], event.location)
            elif idx == 1:
                self.assertEquals(day[1]['title'], event2.title)
                self.assertEquals(day[1]['location'], event2.location)
            else:
                self.assertEquals(len(day), 1)


    def test_when_event_is_repeated_should_return_multiple_events_that_occur_in_week(self):
        url = reverse('EventDashboardFeed')
        user = ViewUserFactory.create()
        today = datetime.date.today()
        repeatedEventProperties = {
            'start_date': today,
            'end_date': today,
            'is_repeat': True,
            'repetition': 'D',
            'ends': today + datetime.timedelta(days=2)
        }
        repeatedEvent = EventFactory.create(**repeatedEventProperties)
        self.login(user)

        response = self.client.get(url)

        for idx, day in enumerate(response.data):
            if idx == 0:
                self.assertEquals(day[1]['title'], repeatedEvent.title)
                self.assertEquals(day[1]['location'], repeatedEvent.location)
            elif idx == 1:
                self.assertEquals(day[1]['title'], repeatedEvent.title)
                self.assertEquals(day[1]['location'], repeatedEvent.location)
            else:
                self.assertEquals(len(day), 1)
