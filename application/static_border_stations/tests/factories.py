import datetime

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyFloat

from accounts.tests.factories import UserFactory, ViewUserDesignation
from dataentry.models import BorderStation, Country, Permission, Region, UserLocationPermission
from static_border_stations.models import Staff, CommitteeMember, Location

class RegionFactory(DjangoModelFactory):
    class Meta:
        model = Region
    
    name = 'Test Region'

class CountryFactory(DjangoModelFactory):
    class Meta:
        model = Country
        
    name = 'Test Country'
    latitude = 1
    longitude = 1
    region = factory.SubFactory(RegionFactory)

class BorderStationFactory(DjangoModelFactory):
    class Meta:
        model = BorderStation
    
    station_code = FuzzyText("", 3)
    station_name = 'Test Borderstation'
    date_established = datetime.date(2015, 2, 19)
    latitude = 1
    longitude = 1
    open = True
    time_zone = 'Asia/Kathmandu'
    operating_country = factory.SubFactory(CountryFactory)


class StaffFactory(DjangoModelFactory):
    class Meta:
        model = Staff

    email = factory.Sequence(lambda n: "staff_first_%d@mail.com" % n)
    first_name = factory.Sequence(lambda n: "staff_first_%d" % n)
    last_name = factory.Sequence(lambda n: "staff_last_%d" % n)
    receives_money_distribution_form = True
    border_station = factory.SubFactory(BorderStationFactory)


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: 'Location {0}'.format(n))
    latitude = FuzzyFloat(0, 20)
    longitude = FuzzyFloat(0, 20)
    border_station = factory.SubFactory(BorderStationFactory)


class CommitteeMemberFactory(DjangoModelFactory):
    class Meta:
        model = CommitteeMember

    email = factory.Sequence(lambda n: "committee_first_%d@mail.com" % n)
    first_name = factory.Sequence(lambda n: "committee_first_%d" % n)
    last_name = factory.Sequence(lambda n: "committee_last_%d" % n)
    receives_money_distribution_form = True
    border_station = factory.SubFactory(BorderStationFactory)

class GenericUser(UserFactory):
    pass
    
class GenericUserWithPermissions():
    @staticmethod
    def create(permission_configuration):
        user = GenericUser.create()
        for config in permission_configuration:
            perm = Permission.objects.get(permission_group=config['group'], action=config['action'])
            
            ulp = UserLocationPermission()
            ulp.account = user
            ulp.permission = perm
            ulp.country = config['country']
            ulp.station = config['station']
            ulp.save()
        
        return user
    
    @staticmethod
    def add_permission(user, permission_configuration):
        for config in permission_configuration:
            perm = Permission.objects.get(permission_group=config['group'], action=config['action'])
            
            ulp = UserLocationPermission()
            ulp.account = user
            ulp.permission = perm
            ulp.country = config['country']
            ulp.station = config['station']
            ulp.save()
            


