from django.conf.urls import url
from accounts.views import *
from rest_framework.authtoken import views

list = {'get': 'list', 'post': 'create'}
detail = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
        url(r'^login/', views.obtain_auth_token),
        url(r'^me/$', CurrentUserView.as_view(), name="CurrentUser"),

        url(r'^account/$', AccountViewSet.as_view(list), name="AccountList"),
        url(r'^account/all/$', AccountViewSet.as_view({'get': 'list_all'}), name="AccountListAll"),
        url(r'^account/(?P<pk>\d+)/$', AccountViewSet.as_view(detail), name='Account'),
        url(r'^account/activate/(?P<activation_key>[a-zA-Z0-9]+)/$', AccountActivateClient.as_view(), name='accountActivation'),
        url(r'^account/resend-activation-email/(?P<pk>\d+)/$', ResendActivationEmailView.as_view(), name='ResendActivationEmail'),

        url(r'^defaultPermissionsSet/$', DefaultPermissionsSetViewSet.as_view(list), name="DefaultPermissionsSets"),
        url(r'^defaultPermissionsSet/(?P<pk>\d+)/$', DefaultPermissionsSetViewSet.as_view(detail), name="DefaultPermissionsSet"),
]
