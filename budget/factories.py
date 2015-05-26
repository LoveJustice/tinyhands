import factory
from factory.django import DjangoModelFactory
import datetime

from budget.models import *


class BorderStationBudgetCalculationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStationBudgetCalculation
