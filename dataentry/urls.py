from django.conf.urls import patterns, url
from dataentry.views import *

urlpatterns = patterns('dataentry.views',
    url(r'^irfs/search/$', interception_record_list_template, name="interceptionrecord_list"),  # Simple render view

    url(r'^irfs/(?P<pk>\d+)/$', InterceptionRecordDetailView.as_view(), name='interceptionrecord_detail'),
    url(r'^irfs/create/$', InterceptionRecordCreateView.as_view(), name='interceptionrecord_create'),
    url(r'^irfs/delete/(?P<pk>\d+)/$', InterceptionRecordDeleteView.as_view(), name='interceptionrecord_delete'),
    url(r'^irfs/update/(?P<pk>\d+)/$', InterceptionRecordUpdateView.as_view(), name='interceptionrecord_update'),
    url(r'^irfs/export/$', InterceptionRecordCSVExportView.as_view(), name='interceptionrecord_csv_export'),
    url(r'^vifs/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    url(r'^vifs/(?P<pk>\d+)/$', VictimInterviewDetailView.as_view(), name='victiminterview_detail'),
    url(r'^vifs/search/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    url(r'^vifs/create/$', VictimInterviewCreateView.as_view(), name='victiminterview_create'),
    url(r'^vifs/delete/(?P<pk>\d+)$', VictimInterviewDeleteView.as_view(), name='victiminterview_delete'),
    url(r'^vifs/update/(?P<pk>\d+)/$', VictimInterviewUpdateView.as_view(), name='victiminterview_update'),
    url(r'^vifs/export/$', VictimInterviewCSVExportView.as_view(), name='victiminterview_csv_export'),
    url(r'^stations/codes/$', StationCodeAPIView.as_view()),

    url(r'^geocodelocation/district/(?P<id>\d+)/$', GeoCodeDistrictAPIView.as_view()),
    url(r'^geocodelocation/district/$', GeoCodeDistrictAPIView.as_view()),
    url(r'^geocodelocations/district-admin/$', DistrictAdminView.as_view(), name='district_admin_page'),
    url(r'^geocodelocations/district-admin/search/$', DistrictAdminView.as_view()),
    url(r'^geocodelocations/district/create/$', DistrictCreateView.as_view(), name='district_create_page'),

    url(r'^geocodelocation/vdc/$', GeoCodeVdcAPIView.as_view()),
    url(r'^geocodelocations/vdc-admin/$', VDCAdminView.as_view(), name='vdc_admin_page'),
    url(r'^geocodelocations/vdc-admin/search/(?P<value>\w+)/$', VDCSearchView.as_view(), name='vdc_admin_search'),
    url(r'^geocodelocations/vdc/create/$', VDCCreateView.as_view(), name='vdc_create_page'),
)
