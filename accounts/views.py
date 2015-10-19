import json

from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin
from extra_views import ModelFormSetView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from util.functions import get_object_or_None
from accounts.models import Account, DefaultPermissionsSet
from accounts.mixins import PermissionsRequiredMixin
from accounts.forms import CreateUnactivatedAccountForm, AccountActivateForm
from accounts.serializers import AccountsSerializer
from rest_api.authentication import HasPermission

@login_required
def home(request):
    return render(request, 'home.html', locals())


class AccountListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ListView):
    model = Account
    permissions_required = ['permission_accounts_manage']


class AccountCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateView):
    model = Account
    form_class = CreateUnactivatedAccountForm
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_manage']

    def get_context_data(self, **kwargs):
        context = super(AccountCreateView, self).get_context_data(**kwargs)
        context['default_permissions_sets'] = json.dumps(list(DefaultPermissionsSet.objects.values()))
        return context


class AccountActivateView(UpdateView):
    model = Account
    template_name = 'accounts/account_activate.html'
    success_url = reverse_lazy('home')
    form_class = AccountActivateForm

    def get_object(self):
        return get_object_or_None(Account, activation_key=self.kwargs['activation_key'])

    def get_context_data(self, **kwargs):
        context = super(AccountActivateView, self).get_context_data(**kwargs)
        if self.object is None or self.object.has_usable_password():
            context['invalid_key'] = True
        return context

    def form_valid(self, form):
        self.object = form.save()
        account = authenticate(username=self.object.email,
                               password=self.request.POST['password1'])
        login(self.request, account)
        return super(AccountActivateView, self).form_valid(form)


class AccountResendActivationEmailView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        RedirectView):
    model = Account
    permanent = False
    permissions_required = ['permission_accounts_manage']
    url = reverse_lazy('account_list')

    def post(self, request, *args, **kwargs):
        account = get_object_or_404(Account, pk=self.kwargs['pk'])
        account.send_activation_email()
        return super(AccountResendActivationEmailView, self).post(request, *args, **kwargs)


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
        'permission_irf_delete',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_vif_delete',
        'permission_accounts_manage',
        'permission_receive_email',
        'permission_border_stations_view',
        'permission_border_stations_add',
        'permission_border_stations_edit',
        'permission_vdc_manage',
        'permission_budget_manage',
    ]
    permissions_required = ['permission_accounts_manage']

    def get_context_data(self, **kwargs):
        context = super(AccountUpdateView, self).get_context_data(**kwargs)
        context['default_permissions_sets'] = json.dumps(list(DefaultPermissionsSet.objects.values()))
        return context


class AccountDeleteView(DeleteView):

    model = Account
    success_url = reverse_lazy('account_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.is_superuser:
            self.object.delete()
        else:
            messages.error(request, "You have no power here!!!")
        return HttpResponseRedirect(self.success_url)


class AccessControlView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ModelFormSetView):
    model = Account
    template_name = 'accounts/access_control.html'
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_manage']
    extra = 0
    fields = [
        'user_designation',
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_irf_delete',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_vif_delete',
        'permission_accounts_manage',
        'permission_receive_email',
        'permission_border_stations_view',
        'permission_border_stations_add',
        'permission_border_stations_edit',
        'permission_vdc_manage',
        'permission_budget_manage',
    ]

    def get_context_data(self, **kwargs):
        context = ModelFormSetView.get_context_data(self, **kwargs)
        context['default_permissions_sets'] = json.dumps(list(DefaultPermissionsSet.objects.values()))
        return context


class AccessDefaultsView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        ModelFormSetView):
    model = DefaultPermissionsSet
    template_name = 'accounts/access_defaults.html'
    success_url = reverse_lazy('account_list')
    permissions_required = ['permission_accounts_manage']
    extra = 0
    fields = [
        'name',
        'permission_irf_view',
        'permission_irf_add',
        'permission_irf_edit',
        'permission_irf_delete',
        'permission_vif_view',
        'permission_vif_add',
        'permission_vif_edit',
        'permission_vif_delete',
        'permission_accounts_manage',
        'permission_border_stations_view',
        'permission_border_stations_add',
        'permission_border_stations_edit',
        'permission_vdc_manage',
        'permission_budget_manage',
    ]


#TODO Currently this view doesn't check to make sure the permission set is
# unused by accounts.  The button to go here is grayed out, but that wouldn't
# stop someone who was bent on deleting.  Come back to this someday.
class AccessDefaultsDeleteView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        DeleteView):
    model = DefaultPermissionsSet
    permissions_required = ['permission_accounts_manage']
    success_url = reverse_lazy('access_defaults')


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']
