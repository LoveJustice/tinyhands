from django.core.urlresolvers import reverse
from django_webtest import WebTest
from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient
from accounts.tests.factories import SuperUserFactory
from budget.factories import BorderStationBudgetCalculationFactory

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
        response = self.client.get('/budget/api/budget_calculations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.post('/budget/api/budget_calculations/', {"border_station": self.border_station.pk})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/budget/api/budget_calculations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # delete the form
        response = self.client.delete('/budget/api/budget_calculations/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 204)

        # count the remaining forms
        response = self.client.get('/budget/api/budget_calculations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def testUpdateBudgetSheet(self):
        response = self.client.post('/budget/api/budget_calculations/', {"border_station": self.border_station.pk})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/budget/api/budget_calculations/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.put('/budget/api/budget_calculations/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water": 2})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/budget/api/budget_calculations/' + str(budget_id) + '/')

        shelter_water = response.data["shelter_water"]
        self.assertEqual(response.data.get('id'), budget_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(shelter_water, 2)


class MoneyDistributionTests(WebTest):
    def setUp(self):
        self.budget_calc_sheet = BorderStationBudgetCalculationFactory()
        self.superuser = SuperUserFactory.create()

    def testViewMoneyDistributionForm(self):
        response = self.app.get(reverse('money_distribution_view', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        self.assertGreater(response.request.url.find(str(self.budget_calc_sheet.pk)), -1)
        self.assertEquals(response.status_code, 200)

    def testContainsMoneyDistributionForm(self):
        response = self.app.get(reverse('money_distribution_view', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        self.assertGreater(response.content.find("budget_calculations/money_distribution_pdf/" + str(self.budget_calc_sheet.pk)), -1)

    def testContainsControllerAndEmailButton(self):
        response = self.app.get(reverse('money_distribution_view', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        self.assertGreater(response.content.find("emailRecipientsCtrl"), -1)  # If it finds the string, it will be >0
        self.assertGreater(response.content.find("main.sendEmails"), -1)

