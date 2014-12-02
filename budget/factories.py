#__author__ = 'dmoore'

import factory
from factory.django import DjangoModelFactory
from budget import models


class BudgetFormFactory(DjangoModelFactory):


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
