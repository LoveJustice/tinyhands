import factory
from factory.django import DjangoModelFactory
import datetime

from dataentry.models import BorderStation
from static_border_stations.models import Staff, CommitteeMember


class BorderStationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStation
    
    station_code = 'TST'
    station_name = 'Test Borderstation'
    date_established = datetime.date(2015, 2, 19)
    latitude = 1
    longitude = 1


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = Staff

    email = factory.Sequence(lambda n: "staff_first_%d@mail.com" % n)
    first_name = factory.Sequence(lambda n: "staff_first_%d" % n)
    last_name = factory.Sequence(lambda n: "staff_last_%d" % n)
    receives_money_distribution_form = True
    border_station = factory.SubFactory(BorderStationFactory)


class CommitteeMemberFactory(DjangoModelFactory):
    class Meta:
        model = CommitteeMember

    email = factory.Sequence(lambda n: "committee_first_%d@mail.com" % n)
    first_name = factory.Sequence(lambda n: "committee_first_%d" % n)
    last_name = factory.Sequence(lambda n: "committee_last_%d" % n)
    receives_money_distribution_form = True
    border_station = factory.SubFactory(BorderStationFactory)
