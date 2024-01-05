from django.conf.urls import url

from static_border_stations.views import *

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update'}
full_detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}


urlpatterns = [
        url(r'^border-station/list/$', BorderStationViewSet.as_view({'get': 'list'}), name="BorderStationList"),
        url(r'^border-station/$', BorderStationViewSet.as_view({'get': 'list_all', 'post': 'create'}), name="BorderStation"),  # Detail
        url(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view(detail_methods), name="BorderStationDetail"),
        url(r'^border-station/(?P<pk>\d+)/location/$', LocationViewSet.as_view({'get': 'retrieve_border_station_locations', 'put': 'update', 'delete': 'destroy'}), name="LocationsForBorderStation"),
        url(r'^border-station/(?P<pk>\d+)/staff/$', StaffViewSet.as_view({'get': 'retrieve_border_station_staff', 'put': 'update', 'delete': 'destroy'}), name="StaffForBorderStation"),
        url(r'^border-station/(?P<pk>\d+)/staff/work/$', StaffViewSet.as_view({'put': 'update_border_station_staff_work'}), name="StaffWork"),
        url(r'^get_station_id/', get_station_id, name='get_station_id'),

        url(r'^committee-member/$', CommitteeMemberViewSet.as_view(list_methods), name="CommitteeMember"),
        url(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view(detail_methods), name="CommitteeMemberDetail"),

        url(r'^location/$', LocationViewSet.as_view(list_methods), name="Location"),
        url(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view(detail_methods), name="LocationDetail"),

        url(r'^staff/$', StaffViewSet.as_view(list_methods), name="Staff"),
        url(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view(detail_methods), name="StaffDetail"),
        url(r'^staff/blank/$', StaffViewSet.as_view({'get':'retrieve_blank'}), name="StaffBlank"),
        url(r'^staff/contract/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve_contract', 'put':'put_contract'}), name="StaffContract"), 
        url(r'^staff/contract/requests/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', StaffViewSet.as_view({'get':'get_contract_project_requests'}), name="StaffContractRequests"), 
        url(r'^staff/knowledge/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve_knowledge', 'put':'put_knowledge'}), name="StaffKnowledge"), 
        url(r'^staff/miscellaneous/$', StaffMiscellaneousViewSet.as_view({'post': 'create'}), name="StaffMiscellaneous"),
        url(r'^staff/miscellaneous/(?P<pk>\d+)/$', StaffMiscellaneousViewSet.as_view(detail_methods), name="StaffMiscellaneousDetail"),
        url(r'^staff-review/$', StaffReviewViewSet.as_view(list_methods), name="StaffReview"),
        url(r'^staff-review/(?P<pk>\d+)/$', StaffReviewViewSet.as_view(full_detail_methods), name="StaffReviewDetail"),
                
        url(r'^timezones/$', TimeZoneViewSet.as_view({'get':'get_time_zones'}), name='TimeZones'),
]
