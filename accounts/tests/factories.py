from factory.django import DjangoModelFactory
import factory

from accounts.models import Account
from accounts.models import DefaultPermissionsSet

class SuperUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        
    permission_irf_view = True
    permission_irf_add = True
    permission_irf_edit = True
    permission_vif_view = True
    permission_vif_add = True
    permission_vif_edit = True
    permission_accounts_manage = True
    permission_receive_email = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    permission_border_stations_edit = True
    permission_vdc_manage = True

class ViewUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        
    permission_irf_view = True
    permission_vif_view = True
    permission_border_stations_view = True
    
class AddUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        
    permission_irf_view = True
    permission_irf_add = True
    permission_vif_view = True
    permission_vif_add = True
    permission_border_stations_view = True
    permission_border_stations_add = True

class UserFactory(DjangoModelFactory):
    class Meta:
        model = Account
        abstract = True
        
    email = "test@test.edu"
    first_name = "test"
    last_name = "test"

class SuperUserFactory(UserFactory):
    permission_irf_view = True
    permission_irf_add = True
    permission_irf_edit = True
    permission_vif_view = True
    permission_vif_add = True
    permission_vif_edit = True
    permission_accounts_manage = True
    permission_receive_email = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    permission_border_stations_edit = True
    permission_vdc_manage = True
    user_designation = factory.SubFactory(SuperUserDesignation)

class ViewUserFactory(UserFactory):
    permission_irf_view = True
    permission_vif_view = True
    permission_border_stations_view = True
    user_designation = factory.SubFactory(ViewUserDesignation)
    
class AddUserFactory(UserFactory):
    permission_irf_view = True
    permission_irf_add = True
    permission_vif_view = True
    permission_vif_add = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    user_designation = factory.SubFactory(AddUserDesignation)