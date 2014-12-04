from django.test import TestCase
from budget import models

class TestModels(TestCase):
    
    def test_budget_1(self):
        var = 1
        var2 = 3
        self.assertEqual(var + var2, 4)

    def test_status_codes(self):
        resp = self.client.get('/budget/budget_calculations/')
        print (resp.status_code)
        self.assertEqual(resp.status_code, 302 or 200)

    def test_border_station_budget_calculation_form_functions(self):
        item = models.BorderStationBudgetCalculation()
        item.shelter_water = 10
        item.shelter_rent = 20
        item.shelter_electricity = 40
        item.shelter_shelter_startup = True
        item.shelter_shelter_startup_amount = 100
        item.shelter_shelter_two_amount = 200
        item.shelter_shelter_two = True
        self.assertEqual(item.shelter_total(), 370)

    # def test_valid_data(self):
        # budget_form = self.app.get(reverse('budget_create'))
        # budget_form.form['email'] = 'dvcolgan@gmail.com'
        # redirect = account_edit.save()
        # self.assertEquals(redirect.status_int, 304)
        # account_list = redirect.follow()

        # original = Account.objects.all()[0]
        # self.client.get(reverse('login'))
        #
        # resp = self.client.get('/portal/dashboard/')
        # self.client.get(reverse('login'))
        # print(resp.status_code)
        # self.assertEqual(resp.status_code, 302)
