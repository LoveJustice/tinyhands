from django.conf.urls import patterns, url
from dataentry.views import *

urlpatterns = patterns('dataentry.views',
    url(r'^irfs/$', InterceptionRecordListView.as_view(), name='interceptionrecord_list'),
    url(r'^irfs/create/$', InterceptionRecordCreateView.as_view(), name='interceptionrecord_create'),
    url(r'^irfs/update/(?P<pk>\d+)/$', InterceptionRecordUpdateView.as_view(), name='interceptionrecord_update'),
    url(r'^irfs/export/$', InterceptionRecordCSVExportView.as_view(), name='interceptionrecord_csv_export'),
    url(r'^vifs/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    url(r'^vifs/create/$', VictimInterviewCreateView.as_view(), name='victiminterview_create'),
    url(r'^vifs/update/(?P<pk>\d+)/$', VictimInterviewUpdateView.as_view(), name='victiminterview_update'),
)
