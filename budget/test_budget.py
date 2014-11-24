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






    #     form = models.BorderStationBudgetCalculation({
    #         'name': "Turanga Leela",
    #         'email': "leela@example.com",
    #         'body': "Hi there",
    #     }, entry=self.entry)
    #     self.assertTrue(form.is_valid())
    #     comment = form.save()
    #     self.assertEqual(comment.name, "Turanga Leela")
    #     self.assertEqual(comment.email, "leela@example.com")
    #     self.assertEqual(comment.body, "Hi there")
    #     self.assertEqual(comment.entry, self.entry)
