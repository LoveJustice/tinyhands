import factory
from factory.django import DjangoModelFactory
import datetime

from dataentry.models import BorderStation

class BorderStationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStation
    
    station_code = 'TST'
    station_name = 'Test Borderstation'
    date_established = datetime.date(2015,2,19)
    latitude = 1
    longitude = 1