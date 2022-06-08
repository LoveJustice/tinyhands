from django.test import TestCase
from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.models import BorderStationBudgetCalculation, OtherBudgetItemCost, StaffBudgetItem


class BorderStationBudgetCalculationTests(TestCase):
    fixtures = ['initial-required-data/Region.json','initial-required-data/Country.json', 'initial-required-data/Permission.json']
    def setUp(self):
        self.target = BorderStationBudgetCalculationFactory()

    def test_travel_total_calculates_correct_value(self):
        fields = [
            self.target.travel_extra_items_total(),
            self.target.staff_project_items_total('Travel', self.target.border_station)
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.travel_total(), expected_total)

    def test_administration_total_calculates_correct_value(self):
        fields = [
            self.target.administration_intercepts_total(),
            self.target.administration_meetings_total(),
            self.target.travel_manager_chair_total(),
            self.target.communication_manager_chair_total(),
            self.target.administration_extra_items_total()
        ]
        expected_total = sum(fields)

        self.assertEqual(self.target.administration_total(), expected_total)

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
        expected_total = sum([item.cost for item in self.target.staffbudgetitem_set.filter(work_project=self.target.border_station).exclude(type_name='Travel')])
        expected_total += self.target.other_project_items_total(BorderStationBudgetCalculation.STAFF_BENEFITS, self.target.border_station)

        self.assertEqual(self.target.salary_and_benefits_total(self.target.border_station), expected_total)
