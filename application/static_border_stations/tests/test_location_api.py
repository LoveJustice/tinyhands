from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class LocationTests(RestApiTestCase):
    def setUp(self):
        self.location = LocationFactory.create()
        self.other_location = LocationFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('Location')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        self.login(UnauthorizedBorderStationUser.create())
        url = reverse('Location')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Viewset Methods

    def test_return_all_Locations(self):
        self.login(ViewBorderStationUser.create())
        url = reverse('Location')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)

    def test_create_Location(self):
        self.login(AddBorderStationUser.create())
        url = reverse('Location')

        data = {
            "name": "asdfasdf",
            "latitude": 1,
            "longitude": 1,
            "border_station": self.location.border_station.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data['name'], response.data['name'])

    def test_get_Location(self):
        self.login(ViewBorderStationUser.create())
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.location.name, response.data[0]['name'])

    def test_update_Location(self):
        self.login(EditBorderStationUser.create())
        url = reverse('LocationsForBorderStation', args=[self.location.id])

        data = {
            "name": "asdfasdf",
            "latitude": 1,
            "longitude": 1,
            "border_station": self.location.border_station.id,
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['name'], response.data['name'])
        
    def test_delete_Location(self):
        self.login(DeleteBorderStationUser.create())
        delete_url = reverse('LocationsForBorderStation', args=[self.location.id])
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])

        location_count = len(self.client.get(url).data)

        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        new_location_count = len(self.client.get(url).data)
        url = reverse('LocationsForBorderStation', args=[self.location.border_station.id])
        self.assertNotEqual(location_count, new_location_count)

    def test_get_Location_by_border_station(self):
        for mem in self.other_location:
            mem.border_station = self.location.border_station
            mem.save()

        self.login(DeleteBorderStationUser.create())
        url = reverse('Location') + "?border_station=" + str(self.location.border_station.id)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
