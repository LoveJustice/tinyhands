from django_webtest import WebTest
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient

from static_border_stations.tests.factories import BorderStationFactory



class BudgetCalcApiTests(WebTest):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.border_station = BorderStationFactory()

    def testCreateBudgetSheet(self):
        response = self.client.post('/budget/api/budget_calculations/', {"border_station": self.border_station.pk})
        self.assertEqual(response.status_code, 201)

    def testRemoveBudgetSheet(self):

        response = self.client.post('/budget/api/budget_calculations/', {"border_station": self.border_station.pk})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        # delete the form
        response = self.client.delete('/budget/api/budget_calculations/' + str(budget_id))
        # self.assertEqual(response.status_code, 201)

        # count the remaining forms
        response = self.client.get('/budget/api/budget_calculations/')
        #self.assertEqual(response.status_code, 201)










