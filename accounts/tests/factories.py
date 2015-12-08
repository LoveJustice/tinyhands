import factory
from factory.django import DjangoModelFactory
from accounts.models import Account, Alert
from accounts.models import DefaultPermissionsSet


class SuperUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        django_get_or_create = ('name',)

    name = "Super User"
    permission_irf_view = True
    permission_irf_add = True
    permission_irf_edit = True
    permission_irf_delete = True
    permission_vif_view = True
    permission_vif_add = True
    permission_vif_edit = True
    permission_vif_delete = True
    permission_accounts_manage = True
    permission_receive_email = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    permission_border_stations_edit = True
    permission_vdc_manage = True


class ViewUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        django_get_or_create = ('name',)

    name = "View User"
    permission_irf_view = True
    permission_vif_view = True
    permission_border_stations_view = True


class AddUserDesignation(DjangoModelFactory):
    class Meta:
        model = DefaultPermissionsSet
        django_get_or_create = ('name',)

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
        django_get_or_create = ('name',)

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
    permission_irf_delete = True
    permission_vif_view = True
    permission_vif_add = True
    permission_vif_edit = True
    permission_vif_delete = True
    permission_accounts_manage = True
    permission_receive_email = True
    permission_border_stations_view = True
    permission_border_stations_add = True
    permission_border_stations_edit = True
    permission_vdc_manage = True
    permission_budget_manage = True
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


class VdcUserFactory(UserFactory):
    permission_vdc_manage = True
    user_designation = factory.SubFactory(EditUserDesignation)


class BadVdcUserFactory(UserFactory):
    permission_vdc_manage = False
    user_designation = factory.SubFactory(EditUserDesignation)


class BadIrfUserFactory(UserFactory):
    permission_irf_view = False
    permission_irf_delete = False
    user_designation = factory.SubFactory(EditUserDesignation)


class BadVifUserFactory(UserFactory):
    permission_vif_view = False
    permission_vif_delete = False
    user_designation = factory.SubFactory(EditUserDesignation)


class AlertFactory(DjangoModelFactory):
    class Meta:
        model = Alert

    email_template = "test"
    code = factory.Sequence(lambda n: 'code{0}'.format(n))

    @factory.post_generation
    def permissions_group(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.permissions_group.add(group)

