from django.urls import re_path
from dataentry.views import *

urlpatterns = [
    re_path(r'^irfs/(?P<pk>\d+)/$', InterceptionRecordDetailView.as_view(), name='interceptionrecord_detail'),
    re_path(r'^irfs/create/$', InterceptionRecordCreateView.as_view(), name='interceptionrecord_create'),
    re_path(r'^irfs/irfExists/([A-Z]{3}[0-9]+[A-Z]*)', irfExists, name='IrfExists'),
    re_path(r'^irfs/update/(?P<pk>\d+)/$', InterceptionRecordUpdateView.as_view(), name='interceptionrecord_update'),
    # Create a url that will have a border station argument and will list irfs for that specific BD station

    re_path(r'^vifs/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    re_path(r'^vifs/(?P<pk>\d+)/$', VictimInterviewDetailView.as_view(), name='victiminterview_detail'),
    re_path(r'^vifs/create/$', VictimInterviewCreateView.as_view(), name='victiminterview_create'),
    re_path(r'^vifs/update/(?P<pk>\d+)/$', VictimInterviewUpdateView.as_view(), name='victiminterview_update'),
    re_path(r'^vifs/vifExists/([A-Z]{3}[0-9]+[A-Z]*)', vifExists, name='VifExists'),

    re_path(r'^stations/codes/$', StationCodeAPIView.as_view()),

    re_path(r'^geocodelocation/address1/(?P<id>\d+)/$', GeoCodeAddress1APIView.as_view()),
    re_path(r'^geocodelocation/address1/$', GeoCodeAddress1APIView.as_view()),
    re_path(r'^geocodelocations/address1/create/$', Address1CreateView.as_view(), name='address1_create_page'),

    re_path(r'^geocodelocation/address2/$', GeoCodeAddress2APIView.as_view()),
    re_path(r'^geocodelocations/address2/create/$', Address2CreateView.as_view(), name='address2_create_page')
]
