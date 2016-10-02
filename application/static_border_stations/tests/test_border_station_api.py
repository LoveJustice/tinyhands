from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class BorderStationsTests(RestApiTestCase):
    def setUp(self):
        self.border_station = BorderStationFactory.create()
        self.other_border_stations = BorderStationFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('BorderStations')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    def test_when_authenticated_and_does_not_have_permission_should_deny_access(self):
        self.login(UnauthorizedBorderStationUser.create())
        url = reverse('BorderStations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Viewset Methods

    def test_return_all_BorderStations(self):
        self.login(ViewBorderStationUser.create())
        url = reverse('BorderStations')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_create_BorderStation(self):
        self.login(AddBorderStationUser.create())
        url = reverse('BorderStations')

        data = {
            "station_code": "TXT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['station_name'], response.data['station_name'])

    def test_get_BorderStation(self):
        self.login(EditBorderStationUser.create())
        url = reverse('BorderStationsDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.border_station.station_name, response.data['station_name'])
        self.assertEqual(self.border_station.id, response.data['id'])

    def test_update_BorderStation(self):
        self.login(EditBorderStationUser.create())
        url = reverse('BorderStationsDetail', args=[self.border_station.id])

        data = {
            "id": self.border_station.id,
            "station_code": "TOT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['station_name'], response.data['station_name'])

    def test_delete_BorderStation(self):
        self.login(DeleteBorderStationUser.create())
        url = reverse('BorderStationsDetail', args=[self.border_station.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

