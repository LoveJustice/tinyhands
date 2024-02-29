from django.urls import re_path
from accounts.views import *

list = {'get': 'list', 'post': 'create'}
detail = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
        re_path(r'^login/', ObtainExpiringAuthToken.as_view()),
        re_path(r'^logout/', Logout.as_view(), name='Logout'),
        re_path(r'^me/$', CurrentUserView.as_view(), name="CurrentUser"),

        re_path(r'^account/$', AccountViewSet.as_view(list), name="AccountList"),
        re_path(r'^account/all/$', AccountViewSet.as_view({'get': 'list_all'}), name="AccountListAll"),
        re_path(r'^account/(?P<pk>\d+)/$', AccountViewSet.as_view(detail), name='Account'),
        re_path(r'^account/activate/(?P<activation_key>[a-zA-Z0-9]+)/$', AccountActivateClient.as_view(), name='accountActivation'),
        re_path(r'^account/resend-activation-email/(?P<pk>\d+)/$', ResendActivationEmailView.as_view(), name='ResendActivationEmail'),
        re_path(r'^account/password-reset/$', password_reset, name='PasswordReset'),
        re_path(r'^account/name/(?P<pk>\d+)/$', AccountNameViewSet.as_view({'get':'get_account_name'}), name='AccountName'),

        re_path(r'^defaultPermissionsSet/$', DefaultPermissionsSetViewSet.as_view(list), name="DefaultPermissionsSets"),
        re_path(r'^defaultPermissionsSet/(?P<pk>\d+)/$', DefaultPermissionsSetViewSet.as_view(detail), name="DefaultPermissionsSet"),

        re_path(r'^account/sync-django-accounts-with-auth0-users/$', sync_django_accounts_with_auth0_users, name='SyncDjangoAccountsWithAuth0Users')
]
