from django.core import mail
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django_webtest import WebTest
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory

from accounts.tests.factories import SuperUserFactory
from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.views import MoneyDistributionFormPDFView
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
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk})
        self.assertEqual(response.status_code, 201)

    def testRemoveBudgetSheet(self):
        response = self.client.get('/api/budget/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk})
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
        response = self.client.post('/api/budget/', {"border_station": self.border_station.pk})
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/budget/' + str(budget_id) + '/')
        budget_id = response.data.get('id')
        self.assertEqual(response.status_code, 200)

        response = self.client.put('/api/budget/' + str(budget_id) + '/', {"border_station": self.border_station.pk, "shelter_water": 2})
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
        self.MDFView = MoneyDistributionFormPDFView(kwargs={"pk": str(self.budget_calc_sheet.id)})
        self.client = APIClient()
        self.client.force_authenticate(user=self.superuser)

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

    def testSendingTwoEmails(self):
        self.staff = StaffFactory.create(border_station=self.budget_calc_sheet.border_station)
        self.committee_member = CommitteeMemberFactory.create(border_station=self.budget_calc_sheet.border_station)

        request = self.app.get(reverse('money_distribution_api', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        staff_data = request.json['staff_members']
        committee_data = request.json['committee_members']

        staff_ids = [int(staff['id']) for staff in staff_data]
        committee_ids = [int(committee['id']) for committee in committee_data]

        response = self.client.post('/api/mdf/' + str(self.budget_calc_sheet.pk) + '/', {"budget_calc_id": self.budget_calc_sheet.pk, "staff_ids": staff_ids, "committee_ids": committee_ids})

        self.assertEquals('"Emails Sent!"', response.content)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].to[0], self.staff.email)
        self.assertEquals(mail.outbox[1].to[0], self.committee_member.email)

    def testSendingFourEmails(self):
        self.staff = StaffFactory.create(border_station=self.budget_calc_sheet.border_station)
        self.committee_member = CommitteeMemberFactory.create(border_station=self.budget_calc_sheet.border_station)
        self.staff2 = StaffFactory.create(border_station=self.budget_calc_sheet.border_station)
        self.committee_member2 = CommitteeMemberFactory.create(border_station=self.budget_calc_sheet.border_station)

        request = self.app.get(reverse('money_distribution_api', kwargs={"pk": self.budget_calc_sheet.pk}), user=self.superuser)
        staff_data = request.json['staff_members']
        committee_data = request.json['committee_members']

        staff_ids = [staff['id'] for staff in staff_data]
        committee_ids = [committee['id'] for committee in committee_data]

        response = self.client.post('/api/mdf/' + str(self.budget_calc_sheet.pk) + '/', {"budget_calc_id": self.budget_calc_sheet.pk, "staff_ids": staff_ids, "committee_ids": committee_ids})

        self.assertEquals('"Emails Sent!"', response.content)
        self.assertEquals(len(mail.outbox), 4)
