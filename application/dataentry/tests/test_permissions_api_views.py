import time

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, APIClient
from dataentry.models import Permission, UserLocationPermission, Country, BorderStation, Region
from accounts.models import Account, DefaultPermissionsSet
from accounts.tests.factories import SuperUserFactory



class PermissionTest(APITestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    globalCount = 0
    
    def get_or_create_country(self, name):
        result = None
        try:
            result = Country.objects.get(name=name)
        except:
            tmp = Country()
            tmp.name = name
            tmp.latitude = 0
            tmp.longitude = 0
            tmp.exchange_rate = 1
            tmp.region = Region.objects.get(name='Asia')
            tmp.save()
            result = Country.objects.get(name=name)
        
        return result
    
    def get_or_create_station(self, name, code, country):
        result = None
        try:
            result = BorderStation.objects.get(station_code=code)
        except:
            tmp = BorderStation()
            tmp.station_name = name
            tmp.station_code = code
            tmp.operating_country = country
            tmp.save()
            result = BorderStation.objects.get(station_code=code)
        
        return result
        
    def setUp(self):
        user = SuperUserFactory.create()
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        
        self.globalCount += 1
        self.nepal = self.get_or_create_country('Nepal')
        self.south_africa = self.get_or_create_country('South Africa')
        self.thailand = self.get_or_create_country('Thailand')
        
        self.nepal_bs1 = self.get_or_create_station("nepal1", "NP1", self.nepal)
        self.nepal_bs2 = self.get_or_create_station("nepal2", "NP2", self.nepal)
        self.nepal_bs3 = self.get_or_create_station("nepal3", "NP3", self.nepal)
        self.south_africa_bs = self.nepal_bs3 = self.get_or_create_station("sa", "SA1", self.south_africa)
        self.thailand_bs = self.nepal_bs3 = self.get_or_create_station("thai", "TL1", self.thailand)
        
        self.account = SuperUserFactory.create()
        
        self.permissions = []
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = None
        tmp.station = None
        tmp.permission = Permission.objects.get(permission_group = 'IRF', action='VIEW')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = None
        tmp.station = self.nepal_bs2
        tmp.permission = Permission.objects.get(permission_group = 'IRF', action='ADD')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = None
        tmp.station = self.thailand_bs
        tmp.permission = Permission.objects.get(permission_group = 'IRF', action='ADD')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = None
        tmp.station = self.nepal_bs2
        tmp.permission = Permission.objects.get(permission_group = 'IRF', action='EDIT')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = None
        tmp.station = self.thailand_bs
        tmp.permission = Permission.objects.get(permission_group = 'IRF', action='EDIT')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = self.nepal
        tmp.station = None
        tmp.permission = Permission.objects.get(permission_group = 'VIF', action='VIEW')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = self.nepal
        tmp.station = None
        tmp.permission = Permission.objects.get(permission_group = 'VIF', action='ADD')
        tmp.save()
        self.permissions.append(tmp)
        
        tmp = UserLocationPermission()
        tmp.account = self.account
        tmp.country = self.nepal
        tmp.station = None
        tmp.permission = Permission.objects.get(permission_group = 'VIF', action='EDIT')
        tmp.save()
        self.permissions.append(tmp)
        
        
            
    def test_list_permissions(self):
        url = reverse('Permission')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_permissions = Permission.objects.all()
        self.assertEqual(response.data['count'], len(db_permissions))
    
    def test_list_user_permissions(self):
        url = reverse('UserLocationPermission', args=[self.account.id])
        response = self.client.get(url)
        
    def test_update_user_permissions(self):
        url = reverse('UserLocationPermission', args=[self.account.id])
        new_perm =  {
            "permissions":[
                {
                    "account": self.account.id,
                    "country": None,
                    "station": None,
                    "permission": Permission.objects.get(permission_group = 'IRF', action='VIEW').id
                },
                {
                    "account": self.account.id,
                    "country": None,
                    "station": None,
                    "permission": Permission.objects.get(permission_group = 'ACCOUNTS', action='MANAGE').id
                },
                {
                    "account": self.account.id,
                    "country": None,
                    "station": self.nepal_bs2.id,
                    "permission": Permission.objects.get(permission_group = 'IRF', action='ADD').id
                }
            ]
        }
        response = self.client.put(url, new_perm)
        
    def test_list_user_countries(self):
        url = reverse('UserPermissionCountries', args=[self.account.id])
        response = self.client.get(url)
        self.assertEqual(len(response.data), 18)
    
    def test_list_user_countries_group(self):
        url = reverse('UserPermissionCountries', args=[self.account.id])
        response = self.client.get(url + "?permission_group=" + 'VIF')
        self.assertEqual(len(response.data), 1)
    
    def test_list_user_stations(self):
        url = reverse('UserPermissionStations', args=[self.account.id])
        response = self.client.get(url)
        self.assertEqual(len(response.data), 5)
    
    def test_list_user_stations_nepal(self):
        url = reverse('UserPermissionStations', args=[self.account.id])
        response = self.client.get(url + "?country_id=" + str(self.nepal.id))
        self.assertEqual(len(response.data), 3)
            
    def test_list_user_stations_thailand(self):
        url = reverse('UserPermissionStations', args=[self.account.id])
        response = self.client.get(url + "?country_id=" + str(self.thailand.id))
        self.assertEqual(len(response.data), 1)
        
    def test_permissions_list_global(self):
        url = reverse('UserLocationPermissionList')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['permissions']), 1)
        
    def test_permissions_list_nepal(self):
        url = reverse('UserLocationPermissionList')
        response = self.client.get(url  + "?country_id=" + str(self.nepal.id))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['permissions']), 4)
        
    def test_permissions_list_nepal_bs(self):
        url = reverse('UserLocationPermissionList')
        response = self.client.get(url  + "?station_id=" + str(self.nepal_bs2.id))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['permissions']), 6)