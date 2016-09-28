from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from accounts.models import Account, DefaultPermissionsSet
from accounts.serializers import AccountsSerializer, DefaultPermissionsSetSerializer
from rest_api.authentication import HasPermission


@login_required
def home(request):
    return render(request, 'home.html', locals())


class AccountActivateClient(APIView):
    def get(self, request, activation_key=None):
        account = Account.objects.get(activation_key=activation_key)
        if account and account.has_usable_password():
            return HttpResponse("account_already_active/invalid_key")
        serializer = AccountsSerializer(account)
        return Response(serializer.data)

    def post(self, request, activation_key=None, password1=None, password2=None):
        account = Account.objects.get(activation_key=activation_key)
        if account and account.has_usable_password():
            return HttpResponse("account_already_active/invalid_key")
        elif request.data['password1'] != request.data['password2']:
            return HttpResponse("unmatching_passwords")
        else:
            account.set_password(request.data['password1'])
            account.save()
            return HttpResponse("acount_saved")


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
        if instance.is_used_by_accounts():
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
