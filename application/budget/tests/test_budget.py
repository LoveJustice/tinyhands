from django.test import TestCase
from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffSalary


class BorderStationBudgetCalculationTests(TestCase):

    def setUp(self):
        self.target = BorderStationBudgetCalculationFactory()

    def test_communication_total_calculates_correct_value(self):
        fields = [
            self.target.communication_extra_items_total(),
            self.target.communication_manager_chair_total(),
            self.target.communication_staff_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.communication_total(), expected_total)

    def test_travel_total_calculates_correct_value(self):
        fields = [
            self.target.travel_extra_items_total(),
            self.target.travel_manager_chair_total(),
            self.target.travel_staff_bikes_total(),
            self.target.travel_last_months_expense_for_sending_girls_home,
            self.target.travel_motorbike_amount,
            self.target.travel_plus_other
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.travel_total(), expected_total)

    def test_administration_total_calculates_correct_value(self):
        fields = [
            self.target.administration_intercepts_total(),
            self.target.administration_meetings_total(),
            self.target.administration_booth_amount,
            self.target.administration_registration_amount,
            self.target.administration_extra_items_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.administration_total(), expected_total)

    def test_medical_total_calculates_correct_value(self):
        fields = [
            self.target.medical_last_months_expense,
            self.target.medical_extra_items_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.medical_total(), expected_total)

    def test_miscellaneous_total_calculates_correct_value(self):
        fields = [
            self.target.miscellaneous_extra_items_total(),
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.miscellaneous_total(), expected_total)

    def test_shelter_total_calculates_correct_value(self):
        shelter_fields = [
            self.target.shelter_rent,
            self.target.shelter_electricity,
            self.target.shelter_water,
            self.target.shelter_extra_items_total(),
            self.target.shelter_shelter_startup_amount,
            self.target.shelter_shelter_two_amount
        ]
        expected_total = sum(shelter_fields)

        self.assertEqual(self.target.shelter_total(), expected_total)

    def test_food_and_gas_total_calculates_correct_value(self):
        fields = [
            self.target.food_and_gas_extra_items_total(),
            self.target.food_and_gas_intercepted_girls_total(),
            self.target.food_and_gas_limbo_girls_total(),
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.food_and_gas_total(), expected_total)

    def test_awareness_total_calculates_correct_value(self):
        fields = [
            self.target.awareness_extra_items_total(),
            self.target.awareness_contact_cards_amount,
            self.target.awareness_awareness_party,
            self.target.awareness_sign_boards,
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.awareness_total(), expected_total)

    def test_supplies_total_calculates_correct_value(self):
        fields = [
            self.target.supplies_walkie_talkies_amount,
            self.target.supplies_recorders_amount,
            self.target.supplies_binoculars_amount,
            self.target.supplies_flashlights_amount,
            self.target.supplies_extra_items_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.supplies_total(), expected_total)

    def test_salary_total_calculates_correct_value(self):
        expected_total = sum([item.salary for item in self.target.staffsalary_set.all()])
        expected_total += self.target.other_items_total(BorderStationBudgetCalculation.STAFF)

        self.assertEqual(self.target.salary_total(), expected_total)
