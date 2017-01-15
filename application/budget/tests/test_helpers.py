from django.test import TestCase

from budget.tests.factories import BorderStationBudgetCalculationFactory
from budget.helpers import BudgetLineItem, BudgetTable, MoneyDistributionFormHelper




class BudgetTableTests(TestCase):

    def test_total_should_return_sum_of_item_values(self):
        items = [BudgetLineItem("one", 1), BudgetLineItem("two", 2)]
        target = BudgetTable("Table", items)

        self.assertEqual(target.total, sum([item.value for item in items]))

    def test_height_required_should_equal_correct_height(self):
        items = [BudgetLineItem("one", 1), BudgetLineItem("two", 2)]
        target = BudgetTable("Table", items)

        self.assertEqual(target.height_required, len(items)*18 + 54)


class MoneyDistributionFormHelperTests(TestCase):

    def setUp(self):
        budget = BorderStationBudgetCalculationFactory()
        self.target = MoneyDistributionFormHelper(budget.id)

    def test_sections_should_return_budget_tables_for_each_section(self):
        result = self.target.sections

        self.assertEqual()




