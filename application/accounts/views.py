import json
import pdb

from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, RedirectView, TemplateView
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin
from extra_views import ModelFormSetView
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from util.functions import get_object_or_None
from accounts.models import Account, DefaultPermissionsSet
from accounts.mixins import PermissionsRequiredMixin
from accounts.forms import CreateUnactivatedAccountForm, AccountActivateForm
from accounts.serializers import AccountsSerializer, DefaultPermissionsSetSerializer
from rest_api.authentication import HasPermission

@login_required
def home(request):
    return render(request, 'home.html', locals())


class AccountListView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        TemplateView):
    template_name="accounts/account_list.html"
    permissions_required = ['permission_accounts_manage']


class AccountCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        TemplateView):
    template_name = 'accounts/account_form.html'
    permissions_required = ['permission_accounts_manage']


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

class AccountActivateClient(APIView):
    def get(self, request, activation_key=None):
        account = Account.objects.get(activation_key=activation_key)
        if account and account.has_usable_password():
            account = None
        serializer = AccountsSerializer(account)
        return Response(serializer.data)

    def post(self, request, activation_key=None):
        account = Account.objects.get(activation_key=activation_key)
        account_activated = False
        print(request)
        '''if account and not account.has_usable_password():
            if request.data.account != request.data.id:
                unmatchingPasswords = True;
                return Response(unmatchingPasswords)
            else:
                account.set_password(request.data.password1)
                account.save()
                account_activated = True
        return Response(account_activated)'''

class AccountUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        TemplateView):
    template_name = 'accounts/account_form.html'
    permissions_required = ['permission_accounts_manage']
    fields = []

    def id(self):
        return self.kwargs['pk']


class AccessControlView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        TemplateView):
    template_name = 'accounts/access_control.html'
    permissions_required = ['permission_accounts_manage']


class AccessDefaultsView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        TemplateView):
    template_name = 'accounts/access_defaults.html'
    permissions_required = ['permission_accounts_manage']


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

#Rest Api Views
class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']

    @list_route()
    def list_all(self, request):
        accounts = Account.objects.all()
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

class DefaultPermissionsSetViewSet(ModelViewSet):
    queryset = DefaultPermissionsSet.objects.all()
    serializer_class = DefaultPermissionsSetSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']

    def destroy(self, request, pk=None):
        instance = DefaultPermissionsSet.objects.get(pk=pk)
        if(instance.is_used_by_accounts()):
            error_message = {'detail': 'Permission set is currently used by accounts. It cannot be deleted.'}
            return Response(error_message, status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AccountsSerializer(request.user)
        return Response(serializer.data)

class ResendActivationEmailView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']

    def post(self, request, pk=None):
        email_sent = False
        account = get_object_or_404(Account, pk=pk)
        if not account.has_usable_password():
            account.send_activation_email()
            email_sent = True
        return Response(email_sent)