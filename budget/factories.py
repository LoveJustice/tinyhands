import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger
from budget.models import *

from datetime import date


class BorderStationBudgetCalculationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStationBudgetCalculation

    border_station = factory.SubFactory(BorderStationFactory)


class OtherBudgetItemCostFactory(DjangoModelFactory):
    class Meta:
        model = OtherBudgetItemCost

    name = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    cost = FuzzyInteger(10, 4000)
    form_section = FuzzyInteger(1, 4)
    budget_calc_sheet = factory.SubFactory(BorderStationBudgetCalculationFactory)


class StaffSalaryFactory(DjangoModelFactory):
    class Meta:
        model = StaffSalary

    full_name = factory.Sequence(lambda n: 'John Doe {0}'.format(n))
    age = FuzzyInteger(20, 40)
    phone_contact = str(FuzzyInteger(100000000000,999999999999).fuzz())
    photo = 'foo.png'
    gender = 'm'
    interception_record = factory.SubFactory(IrfFactory)
    kind = 'v'


class BorderStationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStation


