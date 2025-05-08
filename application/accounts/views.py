import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import filters as fs
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken

from util.auth0 import get_auth0_users, update_django_user_if_exists
from .models import ExpiringToken


from accounts.models import Account, DefaultPermissionsSet, make_activation_key
from accounts.serializers import AccountsSerializer, DefaultPermissionsSetSerializer
from rest_api.authentication import HasPermission


logger = logging.getLogger(__name__)

class AccountViewSet(ModelViewSet):
    queryset = Account.objects.filter(is_active=True)
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('first_name','last_name',)
    ordering_fields = ('last_name', 'first_name',)
    ordering = ('first_name','last_name')

    @action(detail=False)
    def list_all(self, request):
        accounts = Account.objects.all()
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

"""
    Allow retrieval of account names for accounts that do not have account management
    permissions, but do have IRF form permissions.  This is used to retrieve the names
    for display in the IRF verifications.
"""
class AccountNameViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = []

    def get_account_name(self, request, pk):
        mod = __import__('dataentry.models.user_location_permission', fromlist=['UserLocationPermission'])
        form_class = getattr(mod, 'UserLocationPermission', None)
        permissions = form_class.objects.filter(account__id=request.user.id, permission__permission_group='IRF')
        if len(permissions) < 1:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        account = Account.objects.get(id=pk)
        if account is not None:
            account_name = account.first_name + ' ' + account.last_name
        else:
            account_name = ''
        return Response(account_name)

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

class AuthenticateRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def sync_django_accounts_with_auth0_users(request):
    logger.info('Start syncing django accounts with auth0 users')
    auth0_users = get_auth0_users()
    for auth0_user in auth0_users:
        django_account = update_django_user_if_exists(auth0_user)
    logger.info('Finished syncing django accounts with auth0 users')
    return Response(status=status.HTTP_200_OK)
