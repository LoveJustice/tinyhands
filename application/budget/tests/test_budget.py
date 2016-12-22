from django.test import TestCase
from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.models import OtherBudgetItemCost, StaffSalary


class TestModels(TestCase):
    def test_budget_1(self):
        var = 1
        var2 = 3
        self.assertEqual(var + var2, 4)

    def test_border_station_budget_calculation_form_functions(self):
        item = BorderStationBudgetCalculationFactory.create()

        # Shelter
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
        shelter_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=5, name="extra-Shelter", cost=100)
        self.assertEqual(item.shelter_total(), 170)

        # Food and Gas
        item.food_and_gas_number_of_intercepted_girls = 5
        item.food_and_gas_number_of_intercepted_girls_multiplier_before = 100
        item.food_and_gas_number_of_intercepted_girls_multiplier_after = 3
        item.food_and_gas_limbo_girls_multiplier = 100
        item.food_and_gas_number_of_limbo_girls = 10
        item.food_and_gas_number_of_days = 20
        self.assertEqual(item.food_and_gas_total(), 21500)
        food_gas_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=6, name="extra-foodGas", cost=100)
        self.assertEqual(item.food_and_gas_total(), 21600)

        # Awareness
        item.awareness_contact_cards = True
        item.awareness_contact_cards_amount = 5
        item.awareness_awareness_party_boolean = True
        item.awareness_awareness_party = 10
        item.awareness_sign_boards_boolean = True
        item.awareness_sign_boards = 20
        self.assertEqual(item.awareness_total(), 35)
        item.awareness_contact_cards = False
        item.awareness_awareness_party_boolean = False
        item.awareness_sign_boards_boolean = False
        self.assertEqual(item.awareness_total(), 0)
        awareness_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=3, name="extra-Awareness", cost=100)
        self.assertEqual(item.awareness_total(), 100)

        # Supplies
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
        supplies_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=4, name="extra-Supplies", cost=100)
        self.assertEqual(item.supplies_total(), 100)

        # Communication
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
        communication_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=7, name="extra-Communication", cost=100)
        self.assertEqual(item.communication_total(), 3600)

        # Travel
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
        item.travel_chair_with_bike = False
        item.travel_manager_with_bike = False
        item.travel_motorbike = False
        self.assertEqual(item.travel_total(), 1020)
        travel_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=1, name="extra-Travel", cost=100)
        self.assertEqual(item.travel_total(), 1120)

        # Administration
        item.administration_booth = True
        item.administration_booth_amount = 30000
        item.administration_number_of_intercepts_last_month = 3
        item.administration_number_of_intercepts_last_month_adder = 1000
        item.administration_number_of_intercepts_last_month_multiplier = 10
        item.administration_number_of_meetings_per_month = 4
        item.administration_number_of_meetings_per_month_multiplier = 600
        item.administration_registration = True
        item.administration_registration_amount = 2000
        extra_admin = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=10, name="extra-Admin", cost=100)

        self.assertEqual(item.administration_total(), 35530)
        item.administration_booth = False
        item.administration_registration = False
        self.assertEqual(item.administration_total(), 3530)

        # Staff
        staff = StaffSalary.objects.create(budget_calc_sheet=item, salary=1000)
        extra_8 = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=8, name="extra-Staff", cost=100)
        self.assertEqual(item.salary_total(), 1100)

        # Medical
        item.medical_last_months_expense = 500
        extra_medical = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=9, name="extra-Medical", cost=100)

        self.assertEqual(item.medical_total(), 600)

        # Miscellaneous
        item.miscellaneous_number_of_intercepts_last_month = 5
        item.miscellaneous_number_of_intercepts_last_month_multiplier = 300
        self.assertEqual(item.miscellaneous_total(), 1500)
        misc_extra = OtherBudgetItemCost.objects.create(budget_item_parent=item, form_section=2, name="extra-Miscellaneous", cost=100)
        self.assertEqual(item.miscellaneous_total(), 1600)

        # Station Total
        self.assertEqual(item.station_total(), 33520)