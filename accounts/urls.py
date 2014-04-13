from django.conf.urls import patterns, url
from accounts.views import *

urlpatterns = patterns('accounts.views',
    url(r'^$', AccountListView.as_view(), name='account_list'),
    url(r'^create/$', AccountCreateView.as_view(), name='account_create'),
    url(r'^update/(?P<pk>\d+)/$', AccountUpdateView.as_view(), name='account_update'),
    url(r'^permissions-matrix/$', PermissionsMatrixView.as_view(), name='permissions_matrix'),
    url(r'^access-defaults/$', AccessDefaultsView.as_view(), name='access_defaults'),
    url(r'^access-defaults-delete/(?P<pk>\d+)/$', AccessDefaultsDeleteView.as_view(), name='access_defaults_delete'),
)
