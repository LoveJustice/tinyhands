from django.test import TestCase
from budget import models
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class TestSelenium(TestCase):

    def test_login(self):
        driver = webdriver.Firefox()
        driver.maximize_window()
        driver.get("http://127.0.0.1:8000/login/?next=/")
        id_username = driver.find_element_by_id('id_username')
        id_username.clear()
        id_username.send_keys("dvcolgan@gmail.com")
        id_password = driver.find_element_by_id('id_password')
        id_password.clear()
        id_password.send_keys("password")
        id_password.submit()
        #submit = driver.find_elements_by_class_name('btn')
        #submit.click()


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
        item.shelter_shelter_startup = False
        item.shelter_shelter_two = False
        self.assertEqual(item.shelter_total(), 70)

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
        item.awareness_contact_cards = False
        item.awareness_awareness_party_boolean = False
        item.awareness_sign_boards_boolean = False
        self.assertEqual(item.awareness_total(), 0)

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
        item.supplies_walkie_talkies_boolean = False
        item.supplies_recorders_boolean = False
        item.supplies_binoculars_boolean = False
        item.supplies_flashlights_boolean = False
        self.assertEqual(item.supplies_total(), 0)


        #Communication
        item.communication_chair = True
        item.communication_chair_amount = 1000
        item.communication_manager = True
        item.communication_manager_amount = 1000
        item.communication_number_of_staff_with_walkie_talkies = 5
        item.communication_number_of_staff_with_walkie_talkies_multiplier = 100
        item.communication_each_staff = 10
        item.communication_each_staff_multiplier = 300
        self.assertEqual(item.communication_total(), 5500)
        item.communication_chair = False
        item.communication_manager = False
        self.assertEqual(item.communication_total(), 3500)

        #Travel
        item.travel_chair_with_bike = True
        item.travel_chair_with_bike_amount = 2000
        item.travel_manager_with_bike = True
        item.travel_manager_with_bike_amount = 2000
        item.travel_number_of_staff_using_bikes = 5
        item.travel_number_of_staff_using_bikes_multiplier = 100
        item.travel_last_months_expense_for_sending_girls_home = 20
        item.travel_motorbike = True
        item.travel_motorbike_amount = 30000
        item.travel_plus_other = 500
        #self.assertEqual(item.travel_total(), 35020)
        item.travel_chair_with_bike = False
        #self.assertEqual(item.travel_total(), 33020)
        item.travel_manager_with_bike = False
        #self.assertEqual(item.travel_total(), 31020)
        item.travel_motorbike = False
        self.assertEqual(item.travel_total(), 1020)

        #Administration
        item.administration_booth = True
        item.administration_booth_amount = 30000
        item.administration_number_of_intercepts_last_month = 3
        item.administration_number_of_intercepts_last_month_adder = 1000
        item.administration_number_of_intercepts_last_month_multiplier = 10
        item.administration_number_of_meetings_per_month = 4
        item.administration_number_of_meetings_per_month_multiplier = 600
        item.administration_registration = True
        item.administration_registration_amount = 2000
        self.assertEqual(item.administration_total(), 35430)
        item.administration_booth = False
        item.administration_registration = False
        self.assertEqual(item.administration_total(), 3430)

        #Medical
        item.medical_last_months_expense = 500
        self.assertEqual(item.medical_total(), 500)

        #Miscellaneous
        item.miscellaneous_number_of_intercepts_last_month = 5
        item.miscellaneous_number_of_intercepts_last_month_multiplier = 300
        self.assertEqual(item.miscellaneous_total(), 1500)
