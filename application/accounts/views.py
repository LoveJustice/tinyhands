from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import filters as fs
from rest_framework import status
from rest_framework.decorators import list_route, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken

from .models import ExpiringToken


from accounts.models import Account, DefaultPermissionsSet, make_activation_key
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

    def post(self, request, activation_key=None):
        account = Account.objects.get(activation_key=activation_key)
        if account and account.has_usable_password():
            return HttpResponse("account_already_active/invalid_key")
        elif request.data['password1'] != request.data['password2']:
            return HttpResponse("unmatching_passwords")
        else:
            account.set_password(request.data['password1'])
            account.save()
            return HttpResponse("account_saved")


class AccountViewSet(ModelViewSet):
    queryset = Account.objects.all().exclude(is_deleted=True)
    serializer_class = AccountsSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permissions_required = ['permission_accounts_manage']
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    search_fields = ('first_name','last_name',)
    ordering_fields = ('last_name', 'first_name',)
    ordering = ('first_name','last_name')

    @list_route()
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


@api_view(['POST'])
def password_reset(request):
    try:
        # Check if the email belongs to one of the accounts in the database
        email = request.data.get('email','')
        if email == '':
            return Response({"message": "An email was not included in the request!"}, HTTP_400_BAD_REQUEST)

        account = Account.objects.filter(email=email).first()
        if not account:
            return Response({"message": "An account with that email was not found!"}, HTTP_404_NOT_FOUND)

        # Set unusable password and Generate new activation key
        account.set_unusable_password()
        account.activation_key = make_activation_key()
        account.save()

        # Send an activation email to the email
        account.send_activation_email('reset')
        return Response({"message": "Email sent!"}, HTTP_200_OK)
    except:
        return Response({"message": "There was a problem sending the email, please try again!"}, HTTP_500_INTERNAL_SERVER_ERROR)


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
            account.send_activation_email('activate')
            email_sent = True
        return Response(email_sent)

class Logout(APIView):
    def get(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class ObtainExpiringAuthToken(ObtainAuthToken):

    model = ExpiringToken

    def post(self, request):
        """Respond to POSTed username/password with token."""
        serializer = AuthTokenSerializer(data=request.data)

        if serializer.is_valid():
            token, _ = ExpiringToken.objects.get_or_create(
                user=serializer.validated_data['user']
            )

            if token.expired():
                # If the token is expired, generate a new one.
                token.delete()
                token = ExpiringToken.objects.create(
                    user=serializer.validated_data['user']
                )

            login(request, serializer.validated_data['user'], None)
            data = {
                'token': token.key,
                'sessionid': request.session.session_key
            }
            return Response(data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class AuthenticateRequest(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)

