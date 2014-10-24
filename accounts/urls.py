from django.conf.urls import patterns, url
from accounts.views import *

urlpatterns = patterns('accounts.views',
    url(r'^$', AccountListView.as_view(), name='account_list'),

    url(r'^create/$', AccountCreateView.as_view(), name='account_create'),
    url(r'^delete/(?P<pk>\d+)$', AccountDeleteView.as_view(), name='account_delete'),
    url(r'^accounts/activate-account/(?P<activation_key>[a-zA-Z0-9]+)/$', AccountActivateView.as_view(), name='account_activate'),
    url(r'^accounts/resend-activation-email/(?P<pk>\d+)/$', AccountResendActivationEmailView.as_view(), name='account_resend_activation_email'),

    url(r'^update/(?P<pk>\d+)/$', AccountUpdateView.as_view(), name='account_update'),

    url(r'^access-control/$', AccessControlView.as_view(), name='access_control'),
    url(r'^access-defaults/$', AccessDefaultsView.as_view(), name='access_defaults'),
    url(r'^access-defaults-delete/(?P<pk>\d+)/$', AccessDefaultsDeleteView.as_view(), name='access_defaults_delete'),
)
