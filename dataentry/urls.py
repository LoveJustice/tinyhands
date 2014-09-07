from django.conf.urls import patterns, url
from dataentry.views import *

urlpatterns = patterns('dataentry.views',
    url(r'^irfs/$', InterceptionRecordListView.as_view(), name='interceptionrecord_list'),
    url(r'^irfs/(?P<pk>\d+)/$', InterceptionRecordDetailView.as_view(), name='interceptionrecord_detail'),
    url(r'^irfs/search/$', InterceptionRecordListView.as_view(), name="interceptionrecord_list"),
    url(r'^irfs/create/$', InterceptionRecordCreateView.as_view(), name='interceptionrecord_create'),
    url(r'^irfs/update/(?P<pk>\d+)/$', InterceptionRecordUpdateView.as_view(), name='interceptionrecord_update'),
    url(r'^irfs/export/$', InterceptionRecordCSVExportView.as_view(), name='interceptionrecord_csv_export'),
    url(r'^vifs/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    url(r'^vifs/(?P<pk>\d+)/$', VictimInterviewDetailView.as_view(), name='victiminterview_detail'),
    url(r'^vifs/create/$', VictimInterviewCreateView.as_view(), name='victiminterview_create'),
    url(r'^vifs/update/(?P<pk>\d+)/$', VictimInterviewUpdateView.as_view(), name='victiminterview_update'),
    url(r'^vifs/export/$', VictimInterviewCSVExportView.as_view(), name='victiminterview_csv_export'),
)
