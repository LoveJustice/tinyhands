from django.urls import re_path

from static_border_stations.views import *

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update'}


urlpatterns = [
        re_path(r'^border-station/list/$', BorderStationViewSet.as_view({'get': 'list'}), name="BorderStationList"),
        re_path(r'^border-station/$', BorderStationViewSet.as_view({'get': 'list_all', 'post': 'create'}), name="BorderStation"),  # Detail
        re_path(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view(detail_methods), name="BorderStationDetail"),
        re_path(r'^border-station/(?P<pk>\d+)/location/$', LocationViewSet.as_view({'get': 'retrieve_border_station_locations', 'put': 'update', 'delete': 'destroy'}), name="LocationsForBorderStation"),
        re_path(r'^border-station/(?P<pk>\d+)/staff/$', StaffViewSet.as_view({'get': 'retrieve_border_station_staff', 'put': 'update', 'delete': 'destroy'}), name="StaffForBorderStation"),
        re_path(r'^border-station/(?P<pk>\d+)/staff/work/$', StaffViewSet.as_view({'put': 'update_border_station_staff_work'}), name="StaffWork"),
        re_path(r'^get_station_id/', get_station_id, name='get_station_id'),

        re_path(r'^committee-member/$', CommitteeMemberViewSet.as_view(list_methods), name="CommitteeMember"),
        re_path(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view(detail_methods), name="CommitteeMemberDetail"),

        re_path(r'^location/$', LocationViewSet.as_view(list_methods), name="Location"),
        re_path(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view(detail_methods), name="LocationDetail"),

        re_path(r'^staff/$', StaffViewSet.as_view(list_methods), name="Staff"),
        re_path(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view(detail_methods), name="StaffDetail"),
        re_path(r'^staff/blank/$', StaffViewSet.as_view({'get':'retrieve_blank'}), name="StaffBlank"),
        
                
        re_path(r'^timezones/$', TimeZoneViewSet.as_view({'get':'get_time_zones'}), name='TimeZones'),
]
