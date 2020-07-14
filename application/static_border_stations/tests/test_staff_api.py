from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class StaffTests(RestApiTestCase):
    fixtures = ['initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.staff = StaffFactory.create()
        self.other_staff = StaffFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('Staff')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])


    # Viewset Methods

    def test_create_Staff(self):
        usr = GenericUserWithPermissions.create([{'group':'STATIONS', 'action':'VIEW', 'country': None, 'station': None},{'group':'STATIONS', 'action':'ADD', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('Staff')

        data = {
            "email": "TEST@TEST.COM",
            "first_name": "asdf",
            "last_name": "asdf",
            "phone": "204-123-123",
            "position": "asdf",
            "receives_money_distribution_form": True,
            "border_station": self.staff.border_station_id,
            "first_date":"2019-03-15",
            "last_date":None,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data['email'], response.data['email'])

    def test_get_Staff(self):
        usr = GenericUserWithPermissions.create([{'group':'STATIONS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('StaffForBorderStation', args=[self.staff.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.staff.email, response.data[0]['email'])

    def test_update_Staff(self):
        usr = GenericUserWithPermissions.create([{'group':'STATIONS', 'action':'VIEW', 'country': None, 'station': None},{'group':'STATIONS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('StaffDetail', args=[self.staff.id])

        data = {
            "email": "TEST@TEST.COM",
            "first_name": "asdf",
            "last_name": "asdf",
            "phone": "204-123-123",
            "position": "asdf",
            "receives_money_distribution_form": True,
            "border_station": self.staff.border_station_id,
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['email'], response.data['email'])

    def test_delete_Staff(self):
        usr = GenericUserWithPermissions.create([{'group':'STATIONS', 'action':'VIEW', 'country': None, 'station': None},{'group':'STATIONS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
        delete_url = reverse('StaffDetail', args=[self.staff.id])
        url = reverse('StaffForBorderStation', args=[self.staff.border_station.id])

        staff_count = len(self.client.get(url).data)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_Staff_by_border_station(self):
        usr = GenericUserWithPermissions.create([{'group':'STATIONS', 'action':'VIEW', 'country': None, 'station': None},])
        for mem in self.other_staff:
            mem.border_station = self.staff.border_station
            mem.save()

        self.login(usr)
        url = reverse('StaffForBorderStation', args=[self.staff.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
