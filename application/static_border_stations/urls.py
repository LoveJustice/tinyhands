from django.conf.urls import url

from dataentry.views import get_station_id
from static_border_stations.views import *

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}


urlpatterns = [
        # Border Station
        url(r'^border-station/$', BorderStationViewSet.as_view({'get':'list_all', 'post':'create'}), name="BorderStations"), # Detail
        url(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view(detail_methods), name="BorderStation"),
        url(r'^get_station_id/', get_station_id, name='get_station_id'),

        # Committee Members
        url(r'^committee-member/$', CommitteeMemberViewSet.as_view(list_methods), name="CommitteeMembers"),
        url(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view(detail_methods), name="CommitteeMember"),

        # Locations
        url(r'^location/$', LocationViewSet.as_view(list_methods), name="Locations"),
        url(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view(detail_methods), name="Location"),

        # Staff
        url(r'^staff/$', StaffViewSet.as_view(list_methods), name="AllStaff"),
        url(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view({'get': 'staff_retrieve', 'put': 'update', 'delete': 'destroy'}), name="Staff"),

        # TODO: I think this is used in the IRF and VIF to find staff
        url(r'^api/border-stations/(?P<pk>\d+)/$', StaffViewSet.as_view({'get': 'staff_retrieve', 'post': 'create', 'put': 'update', 'delete': 'destroy'}), name="staff_detail_api")
]
