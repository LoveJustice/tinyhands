from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin
from extra_views import ModelFormSetView

from accounts.models import Account, DefaultPermissionsSet
from accounts.mixins import PermissionsRequiredMixin
from accounts.forms import CreateAccountForm


@login_required
def home(request):
    return render(request, 'home.html', locals())


class AccountListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ListView):
    model = Account
    permissions_required = ['permission_accounts_view']


class AccountCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateView):
    model = Account
    form_class = CreateAccountForm
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_add']


class AccountUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateView):
    model = Account
    success_url = reverse_lazy('account_list')
    fields = [
        'email',
        'first_name',
        'last_name',
        'user_designation',
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_accounts_view',
        'permission_accounts_add',
        'permission_accounts_edit',
        'permission_accounts_defaults',
    ]
    permissions_required = ['permission_accounts_edit']


class PermissionsMatrixView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ModelFormSetView):
    model = Account
    template_name = 'accounts/permissions_matrix.html'
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_edit']
    extra = 0
    fields = [
        'user_designation',
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_accounts_view',
        'permission_accounts_add',
        'permission_accounts_edit',
        'permission_accounts_defaults',
    ]


class AccessDefaultsView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ModelFormSetView):
    model = DefaultPermissionsSet
    template_name = 'accounts/access_defaults.html'
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_defaults']
    extra = 0
    fields = [
        'name',
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_accounts_view',
        'permission_accounts_add',
        'permission_accounts_edit',
        'permission_accounts_defaults',
    ]


class AccessDefaultsDeleteView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        DeleteView):
    model = DefaultPermissionsSet
    permissions_required = ['permission_accounts_defaults']
    success_url = reverse_lazy('access_defaults')
