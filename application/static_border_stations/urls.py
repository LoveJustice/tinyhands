from django.conf.urls import url

from static_border_stations.views import *

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}


urlpatterns = [
        url(r'^border-station/$', BorderStationViewSet.as_view({'get': 'list_all', 'post': 'create'}), name="BorderStation"),  # Detail
        url(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view(detail_methods), name="BorderStationDetail"),
        url(r'^get_station_id/', get_station_id, name='get_station_id'),

        url(r'^committee-member/$', CommitteeMemberViewSet.as_view(list_methods), name="CommitteeMember"),
        url(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view(detail_methods), name="CommitteeMemberDetail"),

        url(r'^location/$', LocationViewSet.as_view(list_methods), name="Location"),
        url(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view({'get': 'location_retrieve'}), name="LocationDetail"),

        url(r'^staff/$', StaffViewSet.as_view(list_methods), name="Staff"),
        url(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view({'get': 'staff_retrieve', 'put': 'update', 'delete': 'destroy'}), name="StaffDetail"),
]
