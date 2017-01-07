from django.conf.urls import url
from dataentry.views import *

urlpatterns = [
    url(r'^irfs/(?P<pk>\d+)/$', InterceptionRecordDetailView.as_view(), name='interceptionrecord_detail'),
    url(r'^irfs/create/$', InterceptionRecordCreateView.as_view(), name='interceptionrecord_create'),
    url(r'^irfs/irfExists/([A-Z]{3}[0-9]+[A-Z]*)', irfExists, name='IrfExists'),
    url(r'^irfs/update/(?P<pk>\d+)/$', InterceptionRecordUpdateView.as_view(), name='interceptionrecord_update'),
    # Create a url that will have a border station argument and will list irfs for that specific BD station

    url(r'^vifs/$', VictimInterviewListView.as_view(), name='victiminterview_list'),
    url(r'^vifs/(?P<pk>\d+)/$', VictimInterviewDetailView.as_view(), name='victiminterview_detail'),
    url(r'^vifs/create/$', VictimInterviewCreateView.as_view(), name='victiminterview_create'),
    url(r'^vifs/update/(?P<pk>\d+)/$', VictimInterviewUpdateView.as_view(), name='victiminterview_update'),
    url(r'^vifs/vifExists/([A-Z]{3}[0-9]+[A-Z]*)', vifExists, name='VifExists'),

    url(r'^stations/codes/$', StationCodeAPIView.as_view()),

    url(r'^geocodelocation/address1/(?P<id>\d+)/$', GeoCodeAddress1APIView.as_view()),
    url(r'^geocodelocation/address1/$', GeoCodeAddress1APIView.as_view()),
    url(r'^geocodelocations/address1/create/$', Address1CreateView.as_view(), name='address1_create_page'),

    url(r'^geocodelocation/address2/$', GeoCodeAddress2APIView.as_view()),
    url(r'^geocodelocations/address2/create/$', Address2CreateView.as_view(), name='address2_create_page')
]
