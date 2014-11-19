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
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get('/budget/budget_calculations/create/')
        self.assertEqual(resp.status_code, 302)

    # def test_valid_data(self):
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
