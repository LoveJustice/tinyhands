from django.conf.urls import url
from accounts.views import *

urlpatterns = [
    url(r'^$', AccountListView.as_view(), name='account_list'),

    url(r'^create/$', AccountCreateView.as_view(), name='account_create'),
    url(r'^accounts/activate-account/(?P<activation_key>[a-zA-Z0-9]+)/$', AccountActivateView.as_view(), name='account_activate'),

    url(r'^update/(?P<pk>\d+)/$', AccountUpdateView.as_view(), name='account_update'),

    url(r'^access-control/$', AccessControlView.as_view(), name='access_control'),
    url(r'^access-defaults/$', AccessDefaultsView.as_view(), name='access_defaults'),
]
