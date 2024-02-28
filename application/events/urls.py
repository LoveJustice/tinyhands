from django.urls import re_path

from events.views import EventViewSet

urlpatterns = [
        re_path(r'^event/$', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name="EventList"),
        re_path(r'^event/(?P<pk>\d+)/$', EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='Event'),
        re_path(r'^event/all/$', EventViewSet.as_view({'get': 'list_all'}), name="EventListAll"),
        re_path(r'^event/feed/calendar/$', EventViewSet.as_view({'get': 'calendar_feed'}), name='EventCalendarFeed'),
        re_path(r'^event/feed/dashboard/$', EventViewSet.as_view({'get': 'dashboard_feed'}), name='EventDashboardFeed'),
]
