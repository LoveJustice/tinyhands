from django.test import TestCase
from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem


class BorderStationBudgetCalculationTests(TestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.target = BorderStationBudgetCalculationFactory()

    def test_communication_total_calculates_correct_value(self):
        fields = [
            self.target.communication_extra_items_total(),
            self.target.communication_manager_chair_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.communication_total(), expected_total)

    def test_travel_total_calculates_correct_value(self):
        fields = [
            self.target.travel_extra_items_total(),
            self.target.travel_manager_chair_total(),
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.travel_total(), expected_total)

    def test_administration_total_calculates_correct_value(self):
        fields = [
            self.target.administration_intercepts_total(),
            self.target.administration_meetings_total(),
            self.target.booth_amount,
            self.target.office_amount,
            self.target.administration_extra_items_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.administration_total(), expected_total)

    def test_miscellaneous_total_calculates_correct_value(self):
        fields = [
            self.target.miscellaneous_total(),
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.miscellaneous_total(), expected_total)

    def test_pv_total_calculates_correct_value(self):
        shelter_fields = [
            self.target.shelter_rent_amount,
            self.target.shelter_electricity_amount,
            self.target.shelter_water_amount,
            self.target.pv_extra_items_total(),
            self.target.food_and_gas_intercepted_girls_total(),
            self.target.food_and_gas_limbo_girls_total(),
        ]
        expected_total = sum(shelter_fields)

        self.assertEqual(self.target.pv_total(), expected_total)

    def test_awareness_total_calculates_correct_value(self):
        fields = [
            self.target.awareness_extra_items_total(),
            self.target.contact_cards_amount,
            self.target.awareness_party,
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.awareness_total(), expected_total)

    def test_salary_total_calculates_correct_value(self):
        expected_total = sum([item.cost for item in self.target.staffbudgetitem_set.all()])
        print('test_salary_total_calculates_correct_value', expected_total)
        expected_total += self.target.other_items_total(BorderStationBudgetCalculation.STAFF_BENEFITS)

        self.assertEqual(self.target.staff_and_benefits_total(), expected_total)
