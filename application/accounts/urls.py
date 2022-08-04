from django.conf.urls import url
from accounts.views import *

list = {'get': 'list', 'post': 'create'}
detail = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
        url(r'^login/', ObtainExpiringAuthToken.as_view()),
        url(r'^logout/', Logout.as_view(), name='Logout'),
        url(r'^me/$', CurrentUserView.as_view(), name="CurrentUser"),

        url(r'^account/$', AccountViewSet.as_view(list), name="AccountList"),
        url(r'^account/all/$', AccountViewSet.as_view({'get': 'list_all'}), name="AccountListAll"),
        url(r'^account/(?P<pk>\d+)/$', AccountViewSet.as_view(detail), name='Account'),
        url(r'^account/activate/(?P<activation_key>[a-zA-Z0-9]+)/$', AccountActivateClient.as_view(), name='accountActivation'),
        url(r'^account/resend-activation-email/(?P<pk>\d+)/$', ResendActivationEmailView.as_view(), name='ResendActivationEmail'),
        url(r'^account/password-reset/$', password_reset, name='PasswordReset'),
        url(r'^account/name/(?P<pk>\d+)/$', AccountNameViewSet.as_view({'get':'get_account_name'}), name='AccountName'),

        url(r'^defaultPermissionsSet/$', DefaultPermissionsSetViewSet.as_view(list), name="DefaultPermissionsSets"),
        url(r'^defaultPermissionsSet/(?P<pk>\d+)/$', DefaultPermissionsSetViewSet.as_view(detail), name="DefaultPermissionsSet"),
]
