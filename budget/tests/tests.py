from django.core import mail
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test.testcases import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.test import APIClient

from accounts.tests.factories import SuperUserFactory
from budget.tests.factories import BorderStationBudgetCalculationFactory
from static_border_stations.tests.factories import StaffFactory, CommitteeMemberFactory
from budget.views import MoneyDistributionFormPDFView
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
        self.assertEqual(len(response.data['results']), 0)

        response = self.client.post('/budget/api/budget_calculations/', {"border_station": self.border_station.pk})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/budget/api/budget_calculations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # delete the form
        response = self.client.delete('/budget/api/budget_calculations/' + str(budget_id) + '/')
        self.assertEqual(response.status_code, 204)

        # count the remaining forms
        response = self.client.get('/budget/api/budget_calculations/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

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


class MoneyDistributionWebTests(WebTest, TestCase):
    def setUp(self):
        self.budget_calc_sheet = BorderStationBudgetCalculationFactory()
        self.superuser = SuperUserFactory.create()
        self.MDFView = MoneyDistributionFormPDFView(kwargs={"pk": str(self.budget_calc_sheet.id)})
        self.client = APIClient()

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

    # def testMoneyDistributionForm(self):
    #     import ipdb
    #     ipdb.set_trace()
    #
    #     request = self.app.get(reverse('money_distribution_pdf', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
    #     context_data = self.MDFView.get_context_data()
    #     dispatch = self.MDFView.dispatch(request)
    #
    #     self.assertEquals("application/pdf", request.content_type)
    #     self.assertEquals(context_data['admin_total'], 1000)
    #     self.assertGreater(dispatch.items()[1][1].find('filename=Monthly-Money-Distribution-Form.pdf'), -1)

    def testSendingTwoEmails(self):
        self.staff = StaffFactory(border_station=self.budget_calc_sheet.border_station)
        self.committee_member = CommitteeMemberFactory(border_station=self.budget_calc_sheet.border_station)

        request = self.app.get(reverse('money_distribution_api', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        staff_data = request.json['staff_members']
        committee_data = request.json['committee_members']

        staff_ids = [int(staff['id']) for staff in staff_data]
        committee_ids = [int(committee['id']) for committee in committee_data]

        response = self.client.post('/budget/api/budget_calculations/money_distribution/' + str(self.budget_calc_sheet.pk) + '/', {"budget_calc_id": self.budget_calc_sheet.pk, "staff_ids": staff_ids, "committee_ids": committee_ids})

        self.assertEquals('"Emails Sent!"', response.content)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].to[0], self.staff.email)
        self.assertEquals(mail.outbox[1].to[0], self.committee_member.email)

    def testSendingFourEmails(self):
        self.staff = StaffFactory(border_station=self.budget_calc_sheet.border_station)
        self.committee_member = CommitteeMemberFactory(border_station=self.budget_calc_sheet.border_station)
        self.staff2 = StaffFactory(border_station=self.budget_calc_sheet.border_station)
        self.committee_member2 = CommitteeMemberFactory(border_station=self.budget_calc_sheet.border_station)

        request = self.app.get(reverse('money_distribution_api', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        staff_data = request.json['staff_members']
        committee_data = request.json['committee_members']

        staff_ids = [staff['id'] for staff in staff_data]
        committee_ids = [committee['id'] for committee in committee_data]

        response = self.client.post('/budget/api/budget_calculations/money_distribution/' + str(self.budget_calc_sheet.pk) + '/', {"budget_calc_id": self.budget_calc_sheet.pk, "staff_ids": staff_ids, "committee_ids": committee_ids})

        self.assertEquals('"Emails Sent!"', response.content)
        self.assertEquals(len(mail.outbox), 4)
