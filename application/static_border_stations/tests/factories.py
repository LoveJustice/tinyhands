import factory
from factory.django import DjangoModelFactory
import datetime

from factory.fuzzy import FuzzyText

from accounts.tests.factories import UserFactory, ViewUserDesignation
from dataentry.models import BorderStation
from static_border_stations.models import Staff, CommitteeMember


class BorderStationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStation
    
    station_code = FuzzyText("", 3)
    station_name = 'Test Borderstation'
    date_established = datetime.date(2015, 2, 19)
    latitude = 1
    longitude = 1
    open = True


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


class UnauthorizedBorderStationUser(UserFactory):
    permission_border_stations_view = False
    user_designation = factory.SubFactory(ViewUserDesignation)


class ViewBorderStationUser(UserFactory):
    permission_border_stations_view = True
    user_designation = factory.SubFactory(ViewUserDesignation)


class EditBorderStationUser(UserFactory):
    permission_border_stations_edit = True
    permission_border_stations_view = True
    user_designation = factory.SubFactory(ViewUserDesignation)


class AddBorderStationUser(UserFactory):
    permission_border_stations_add = True
    permission_border_stations_view = True
    user_designation = factory.SubFactory(ViewUserDesignation)


class DeleteBorderStationUser(UserFactory):
    permission_border_stations_delete = True
    permission_border_stations_view = True
    user_designation = factory.SubFactory(ViewUserDesignation)
