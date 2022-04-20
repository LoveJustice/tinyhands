from django.test import TestCase

from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.helpers import BudgetLineItem, BudgetTable, Footnote, MoneyDistributionFormHelper
from budget.models import BorderStationBudgetCalculation


class BudgetTableTests(TestCase):

    def test_total_should_return_sum_of_item_values(self):
        items = [BudgetLineItem("one", 1, ''), BudgetLineItem("two", 2, '')]
        target = BudgetTable("Table", items)

        self.assertEqual(target.total, sum([item.value for item in items]))

    def test_height_required_should_equal_correct_height(self):
        items = [BudgetLineItem("one", 1, ''), BudgetLineItem("two", 2, '')]
        target = BudgetTable("Table", items)

        self.assertEqual(target.height_required, (len(items)+1)*BudgetTable.ROW_HEIGHT + BudgetTable.TITLE_HEIGHT)

    def test_height_required_should_account_for_items_with_multiline_text(self):
        items = [
            BudgetLineItem("one", 1, ''),
            BudgetLineItem("two", 2, ''),
            BudgetLineItem("This is a very long line of text to make sure we calculate correctly", 30, '')
        ]
        target = BudgetTable("Table", items)

        self.assertEqual(target.height_required, (len(items)+3)*BudgetTable.ROW_HEIGHT + BudgetTable.TITLE_HEIGHT)


class MoneyDistributionFormHelperTests(TestCase):

    def setUp(self):
        self.budget = BorderStationBudgetCalculationFactory()
        self.footnote1 = Footnote()
        self.footnote2 = Footnote()
        self.target = MoneyDistributionFormHelper(self.budget, self.budget.border_station, self.footnote1, self.footnote2)

    def test_sections_should_return_budget_tables_for_each_section(self):
        result = self.target.sections

        count = sum(1 for _ in result)

        self.assertEqual(count, 6)

    def test_total_should_return_total_budget_cost(self):
        result = self.target.total

        self.assertEqual(result, self.budget.station_total(self.budget.border_station))

    def test_date_entered_should_return_date_budget_was_entered(self):
        self.assertEqual(self.target.date_entered, self.budget.date_time_entered.date())

    def test_station_name_should_return_budget_station_name(self):
        self.assertEqual(self.target.station_name, self.budget.border_station.station_name)

    def test_staff_salary_items_should_return_list_of_salary_and_benefit_items(self):
        result = self.target.salary_and_benefit_items

        self.assertEqual(len(result), 2)

    def test_travel_items_should_return_list_of_travel_items(self):
        result = self.target.staff_travel_items

        self.assertEqual(len(result), 1)

    def test_administration_items_should_return_list_of_administration_items(self):
        result = self.target.administration_items

        self.assertEqual(len(result), 4)

    def test_shelter_items_should_return_list_of_potential_victim_care_items(self):
        result = self.target.potential_victim_care_items

        self.assertEqual(len(result), 4)

    def test_awareness_items_should_return_list_of_awareness_items(self):
        result = self.target.supplies_and_awareness_items

        self.assertEqual(len(result), 4)

    def test_get_other_items_should_return_other_items_for_section(self):
        result = self.target.get_other_items(BorderStationBudgetCalculation.ADMINISTRATION, self.budget.border_station)

        self.assertEqual(len(result), 1)
