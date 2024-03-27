from django.urls import re_path

from static_border_stations.views import *

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update'}
full_detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}


urlpatterns = [
        re_path(r'^border-station/list/$', BorderStationViewSet.as_view({'get': 'list'}), name="BorderStationList"),
        re_path(r'^border-station/$', BorderStationViewSet.as_view({'get': 'list_all', 'post': 'create'}), name="BorderStation"),  # Detail
        re_path(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view(detail_methods), name="BorderStationDetail"),
        re_path(r'^border-station/(?P<pk>\d+)/location/$', LocationViewSet.as_view({'get': 'retrieve_border_station_locations', 'put': 'update', 'delete': 'destroy'}), name="LocationsForBorderStation"),
        re_path(r'^border-station/(?P<pk>\d+)/staff/$', StaffViewSet.as_view({'get': 'retrieve_border_station_staff', 'put': 'update', 'delete': 'destroy'}), name="StaffForBorderStation"),
        re_path(r'^border-station/(?P<pk>\d+)/staff/work/$', StaffViewSet.as_view({'put': 'update_border_station_staff_work'}), name="StaffWork"),
        re_path(r'^get_station_id/', get_station_id, name='get_station_id'),

        re_path(r'^committee-member/$', CommitteeMemberViewSet.as_view(list_methods), name="CommitteeMember"),
        re_path(r'^committee-member/blank/$', CommitteeMemberViewSet.as_view({'get':'retrieve_blank'}), name="CommitteeMemberBlank"),
        re_path(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view(full_detail_methods), name="CommitteeMemberDetail"),

        re_path(r'^location/$', LocationViewSet.as_view(list_methods), name="Location"),
        re_path(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view(detail_methods), name="LocationDetail"),

        re_path(r'^staff/$', StaffViewSet.as_view(list_methods), name="Staff"),
        re_path(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view(detail_methods), name="StaffDetail"),
        re_path(r'^staff/blank/$', StaffViewSet.as_view({'get':'retrieve_blank'}), name="StaffBlank"),
        re_path(r'^staff/csv/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve_csv'}), name="StaffCsv"),
        re_path(r'^staff/contract/requests/(?P<pk>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', StaffViewSet.as_view({'get':'get_contract_project_requests'}), name="StaffContractRequests"), 
        re_path(r'^staff/attachment/$', StaffAttachmentViewSet.as_view(list_methods), name="StaffAttachment"),
        re_path(r'^staff/attachment/(?P<pk>\d+)/$', StaffAttachmentViewSet.as_view(full_detail_methods), name="StaffAttachmentDetail"),
        re_path(r'^staff/knowledge/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve_knowledge', 'put':'put_knowledge'}), name="StaffKnowledge"), 
        re_path(r'^staff/miscellaneous/$', StaffMiscellaneousViewSet.as_view({'post': 'create'}), name="StaffMiscellaneous"),
        re_path(r'^staff/miscellaneous/(?P<pk>\d+)/$', StaffMiscellaneousViewSet.as_view(detail_methods), name="StaffMiscellaneousDetail"),
        re_path(r'^staff-review/$', StaffReviewViewSet.as_view(list_methods), name="StaffReview"),
        re_path(r'^staff-review/(?P<pk>\d+)/$', StaffReviewViewSet.as_view(full_detail_methods), name="StaffReviewDetail"),
                
        re_path(r'^timezones/$', TimeZoneViewSet.as_view({'get':'get_time_zones'}), name='TimeZones'),
]
