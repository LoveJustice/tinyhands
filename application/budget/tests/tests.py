import datetime
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django_webtest import WebTest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from accounts.tests.factories import SuperUserFactory
from budget.tests.factories import BorderStationBudgetCalculationFactory
from static_border_stations.tests.factories import BorderStationFactory, GenericUserWithPermissions
from static_border_stations.tests.factories import StaffFactory, CommitteeMemberFactory


class BudgetCalcApiTests(WebTest):
    fixtures = ['initial-required-data/Region.json', 'initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'EDIT', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'DELETE', 'country': None, 'station': None},
            ])
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.border_station = BorderStationFactory()

    def testCreateBudgetSheet(self):
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 201)
    
    def testCreateBudgetSheetNoPermission(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-05-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 403)
    
        
    def testCreateBudgetSheetCountry(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': self.border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-05-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 201)
        
    def testCreateBudgetSheetCountryNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-05-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 201)
    
    def testCreateBudgetSheetStation(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': self.border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-06-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 201)
        
    def testCreateBudgetSheetStationNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-06-15T23:53:08.996000Z"})
        self.assertEqual(response.status_code, 201)

    def testRemoveBudgetSheet(self):
        response = self.client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = self.client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 204)

        # count the remaining forms
        response = self.client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
    
    def testRemoveBudgetSheetNoPermission(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 403)

        # count the remaining forms
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        
    def testRemoveBudgetSheetCountry(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': self.border_station.operating_country, 'station': None},
            {'group':'BUDGETS', 'action':'DELETE', 'country': self.border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 204)

        # count the remaining forms
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
    
    def testRemoveBudgetSheetCountryNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'DELETE', 'country': border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 403)

        # count the remaining forms
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
    
    def testRemoveBudgetSheetStation(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': self.border_station},
            {'group':'BUDGETS', 'action':'DELETE', 'country': None, 'station': self.border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 204)

        # count the remaining forms
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
    
    def testRemoveBudgetSheetStationNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'DELETE', 'country': None, 'station': border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = client.delete('/api/budget/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 403)

        # count the remaining forms
        response = client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
    

    def testUpdateBudgetSheet(self):
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/budget/' + str(budget_id) + '/')

        shelter_water_amount = response.data["shelter_water_amount"]
        self.assertEqual(response.data.get('id'), budget_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(shelter_water_amount, '2.00')
    
    def testUpdateBudgetSheetNoPermission(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 403)
    
    def testUpdateBudgetSheetCountry(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'EDIT', 'country': self.border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/budget/' + str(budget_id) + '/')

        shelter_water_amount = response.data["shelter_water_amount"]
        self.assertEqual(response.data.get('id'), budget_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(shelter_water_amount, '2.00')
    
    def testUpdateBudgetSheetCountryNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'EDIT', 'country': border_station.operating_country, 'station': None},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 403)
    
    def testUpdateBudgetSheetStation(self):
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'EDIT', 'country': None, 'station': self.border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.get('/api/budget/' + str(budget_id) + '/')

        shelter_water_amount = response.data["shelter_water_amount"]
        self.assertEqual(response.data.get('id'), budget_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(shelter_water_amount, '2.00')
    
    def testUpdateBudgetSheetStationNoPermission(self):
        border_station = BorderStationFactory()
        user = GenericUserWithPermissions.create([
            {'group':'BUDGETS', 'action':'VIEW', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'ADD', 'country': None, 'station': None},
            {'group':'BUDGETS', 'action':'EDIT', 'country': None, 'station': border_station},
            ])
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water_amount": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 403)

class MoneyDistributionWebTests(WebTest, TestCase):
    def setUp(self):
        self.border_station = BorderStationFactory.create()
        self.budget_calc_sheet = BorderStationBudgetCalculationFactory.create(border_station=self.border_station)
        self.superuser = SuperUserFactory.create()
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def testViewMoneyDistributionForm(self):
        response = self.app.get(reverse('MdfPdf', kwargs={"uuid": self.budget_calc_sheet.mdf_uuid, "mdf_type":"budget"}), user=self.superuser)
        self.assertGreater(response.request.url.find(str(self.budget_calc_sheet.mdf_uuid)), -1)
        self.assertEqual(response.status_code, 200)
