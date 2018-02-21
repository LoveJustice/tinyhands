import datetime
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django_webtest import WebTest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from accounts.tests.factories import SuperUserFactory
from budget.tests.factories import BorderStationBudgetCalculationFactory
from static_border_stations.tests.factories import BorderStationFactory
from static_border_stations.tests.factories import StaffFactory, CommitteeMemberFactory


class BudgetCalcApiTests(WebTest):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = SuperUserFactory.create()
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)
        self.border_station = BorderStationFactory()

    def testCreateBudgetSheet(self):
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
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

    def testUpdateBudgetSheet(self):
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water": 2, "month_year": "2017-04-15T23:53:08.996000Z"})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/budget/' + str(budget_id) + '/')

        shelter_water = response.data["shelter_water"]
        self.assertEqual(response.data.get('id'), budget_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(shelter_water, 2)


class MoneyDistributionWebTests(WebTest, TestCase):
    def setUp(self):
        self.border_station = BorderStationFactory.create()
        self.budget_calc_sheet = BorderStationBudgetCalculationFactory.create(border_station=self.border_station)
        self.superuser = SuperUserFactory.create()
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

    def testViewMoneyDistributionForm(self):
        response = self.app.get(reverse('MdfPdf', kwargs={"uuid": self.budget_calc_sheet.mdf_uuid}), user=self.superuser)
        self.assertGreater(response.request.url.find(str(self.budget_calc_sheet.mdf_uuid)), -1)
        self.assertEquals(response.status_code, 200)
