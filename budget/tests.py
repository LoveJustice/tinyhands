from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone
from django_webtest import WebTest

from budget.factories import *
import ipdb

class BudgetCalcApiTests(WebTest):

    def setUp(self):
        #timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        budgetCalc = BorderStationBudgetCalculationFactory._create()
        other_budget_item = OtherBudgetItemCostFactory._create()

    def test(self):
        ipdb.set_trace()
