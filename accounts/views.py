from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from braces.views import LoginRequiredMixin
from extra_views import ModelFormSetView, InlineFormSet

from accounts.models import Account
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
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_accounts_view',
        'permission_accounts_add',
        'permission_accounts_edit',
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
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_accounts_view',
        'permission_accounts_add',
        'permission_accounts_edit',
    ]
