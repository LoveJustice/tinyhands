from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from static_border_stations.tests.factories import *
from dataentry.models import Country


class RestApiTestCase(APITestCase):
    def login(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)


class BorderStationsTests(RestApiTestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.border_station = BorderStationFactory.create(open=False)
        self.other_border_stations = BorderStationFactory.create_batch(4)

    # Authentication Methods

    def test_when_not_authenticated_should_deny_access(self):
        url = reverse('BorderStation')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])

    # Viewset Methods

    def test_return_all_BorderStations(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStation')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_when_open_param_set_to_true_should_return_open_border_stations(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStation')

        response = self.client.get(url+'?open=true')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_when_open_param_set_to_false_should_return_closed_border_stations(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStation')

        response = self.client.get(url+'?open=false')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_BorderStation_global(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'ADD', 'country': None, 'station': None}])
        self.login(usr)
        country = CountryFactory.create()
        url = reverse('BorderStation')

        data = {
            "station_code": "TXT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "operating_country": country.id,
            "time_zone": "Asia/Kathmandu",
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['station_name'], response.data['station_name'])
    
    def test_create_BorderStation_country(self):
        country = CountryFactory.create()
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'ADD', 'country': country, 'station': None}])
        self.login(usr)
        url = reverse('BorderStation')

        data = {
            "station_code": "TXT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "operating_country": country.id,
            "time_zone": "Asia/Kathmandu",
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(data['station_name'], response.data['station_name'])

    def test_get_BorderStation_global(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None}])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.border_station.station_name, response.data['station_name'])
        self.assertEqual(self.border_station.id, response.data['id'])
        
    def test_get_BorderStation_country(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'VIEW', 'country': self.border_station.operating_country, 'station': None}])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.border_station.station_name, response.data['station_name'])
        self.assertEqual(self.border_station.id, response.data['id'])
        
    def test_get_BorderStation_station(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': self.border_station}])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.border_station.station_name, response.data['station_name'])
        self.assertEqual(self.border_station.id, response.data['id'])

    def test_update_BorderStation_global(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        data = {
            "id": self.border_station.id,
            "station_code": "TOT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "time_zone": "Asia/Kathmandu",
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['station_name'], response.data['station_name'])
    
    def test_update_BorderStation_country(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': self.border_station.operating_country, 'station': None},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        data = {
            "id": self.border_station.id,
            "station_code": "TOT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "time_zone": "Asia/Kathmandu",
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['station_name'], response.data['station_name'])
        
    def test_update_BorderStation_station(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'EDIT', 'country': None, 'station': self.border_station},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        data = {
            "id": self.border_station.id,
            "station_code": "TOT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "time_zone": "Asia/Kathmandu",
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['station_name'], response.data['station_name'])

    def test_delete_BorderStation(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_station_id_when_not_authenticated_should_deny_access(self):
        url = reverse('get_station_id')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn('Authentication credentials were not provided', response.data['detail'])
    
    def test_get_BorderStation_without_permission_should_deny(self):
        usr = GenericUserWithPermissions.create([{'group':'IRF', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_BorderStation_without_country_permission_should_deny(self):
        perm_country = CountryFactory.create()
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': perm_country, 'station': None},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_BorderStation_without_station_permission_should_deny(self):
        perm_station = BorderStationFactory.create()
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': perm_station},])
        self.login(usr)
        url = reverse('BorderStationDetail', args=[self.border_station.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_create_BorderStation_without_permission_should_deny(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        country = CountryFactory.create()
        url = reverse('BorderStation')

        data = {
            "station_code": "TXT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "operating_country": country.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_create_BorderStation_without_country_permission_should_deny(self):
        perm_country = CountryFactory.create()
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},{'group':'PROJECTS', 'action':'VIEW', 'country': perm_country, 'station': None},])
        self.login(usr)
        country = CountryFactory.create()
        url = reverse('BorderStation')

        data = {
            "station_code": "TXT",
            "station_name": 'Test Borderstation123123',
            "date_established": datetime.date(2015, 2, 19),
            "latitude": 1,
            "longitude": 1,
            "open": True,
            "operating_country": country.id,
        }

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_station_id__no_code_should_return_neg1(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('get_station_id')
        response = self.client.get(url + "?code=")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(-1, response.data)

    def test_get_station_id__invalid_code_should_return_neg1(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('get_station_id')
        response = self.client.get(url + "?code=ZZZ")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(-1, response.data)

    def test_get_station_id__valid_code_should_return_border_station_id(self):
        usr = GenericUserWithPermissions.create([{'group':'PROJECTS', 'action':'VIEW', 'country': None, 'station': None},])
        self.login(usr)
        url = reverse('get_station_id')
        response = self.client.get(url + "?code=" + self.border_station.station_code)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.border_station.id, response.data)
