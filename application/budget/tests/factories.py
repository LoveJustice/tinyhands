import datetime
import factory
import pytz
from factory.django import DjangoModelFactory
from budget.models import BorderStationBudgetCalculation
from static_border_stations.tests.factories import BorderStationFactory


class BorderStationBudgetCalculationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStationBudgetCalculation

    border_station = factory.SubFactory(BorderStationFactory)
    month_year = datetime.datetime(2015, 5, 5, 5, tzinfo=pytz.UTC)
