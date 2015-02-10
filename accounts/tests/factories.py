import factory
from factory.django import DjangoModelFactory

from accounts.models import Account
from accounts.models import DefaultPermissionsSet

class SuperUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet

    name = "Super User"
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

    name = "View User"
    permission_irf_view = True
    permission_vif_view = True
    permission_border_stations_view = True
    
class AddUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet

    name = "Add User"
    permission_irf_view = True
    permission_irf_add = True
    permission_vif_view = True
    permission_vif_add = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    
class EditUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet

    name = "Edit User"
    permission_irf_view = True
    permission_irf_edit = True
    permission_vif_view = True
    permission_vif_edit = True
    permission_border_stations_view = True
    permission_border_stations_edit = True

class UserFactory(DjangoModelFactory):
    class Meta:
        model = Account
        abstract = True
        
    email = factory.Sequence(lambda n: 'test{0}@test.com'.format(n))
    first_name = factory.Sequence(lambda n: 'test{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'test{0}'.format(n))

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
    
class EditUserFactory(UserFactory):
    permission_irf_view = True
    permission_irf_edit = True
    permission_vif_view = True
    permission_vif_edit = True
    permission_border_stations_view = True
    permission_border_stations_edit = True
    user_designation = factory.SubFactory(EditUserDesignation)