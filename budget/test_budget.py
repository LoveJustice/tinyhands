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

        #Shelter
        item.shelter_water = 10
        item.shelter_rent = 20
        item.shelter_electricity = 40
        item.shelter_shelter_startup = True
        item.shelter_shelter_startup_amount = 100
        item.shelter_shelter_two_amount = 200
        item.shelter_shelter_two = True
        self.assertEqual(item.shelter_total(), 370)

        #Food and Gas
        item.food_and_gas_number_of_intercepted_girls = 5
        item.food_and_gas_number_of_intercepted_girls_multiplier_before = 100
        item.food_and_gas_number_of_intercepted_girls_multiplier_after = 3
        item.food_and_gas_limbo_girls_multiplier = 100
        item.food_and_gas_number_of_limbo_girls = 10
        item.food_and_gas_number_of_days = 20
        self.assertEqual(item.food_and_gas_total(), 21500)

        #Awareness
        item.awareness_contact_cards = True
        item.awareness_contact_cards_boolean_amount = 4000
        item.awareness_contact_cards_amount = 5
        item.awareness_awareness_party_boolean = True
        item.awareness_awareness_party = 10
        item.awareness_sign_boards_boolean = True
        item.awareness_sign_boards = 20
        self.assertEqual(item.awareness_total(), 4035)

        #Supplies
        item.supplies_walkie_talkies_boolean = True
        item.supplies_walkie_talkies_amount = 20
        item.supplies_recorders_boolean = True
        item.supplies_recorders_amount = 40
        item.supplies_binoculars_boolean = True
        item.supplies_binoculars_amount = 60
        item.supplies_flashlights_boolean = True
        item.supplies_flashlights_amount = 5
        self.assertEqual(item.supplies_total(), 125)