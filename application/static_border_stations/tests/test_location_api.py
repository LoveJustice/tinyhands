from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class LocationTests(RestApiTestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.location = LocationFactory.create()
        self.other_location = LocationFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('Location')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    # Viewset Methods

    def test_return_all_Locations(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('Location')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_create_Location(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'ADD', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('Location')

        data = {
            "name": "asdfasdf",
            "latitude": 1,
            "longitude": 1,
            "location_type":"monitoring",
            "border_station": self.location.border_station.id,
            "first_date":"2019-03-15",
            "last_date":None,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data['name'], response.data['name'])

    def test_get_Location(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.location.name, response.data[0]['name'])

    def test_update_Location(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('LocationDetail', args=[self.location.id])

        data = {
            "name": "asdfasdf",
            "latitude": 1,
            "longitude": 1,
            "location_type":"office",
            "border_station": self.location.border_station.id,
            "first_date":"2019-03-15",
            "last_date":"2020-05-15",
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], response.data['name'])
        
    def test_delete_Location(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': None}])
        self.login(usr)
        delete_url = reverse('LocationDetail', args=[self.location.id])
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])

        location_count = len(self.client.get(url).data)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_Location_by_border_station(self):
        for mem in self.other_location:
            mem.border_station = self.location.border_station
            mem.save()

        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
