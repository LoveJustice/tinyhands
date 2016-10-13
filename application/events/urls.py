from django.conf.urls import url

from events.views import EventViewSet

urlpatterns = [
        url(r'^event/$', EventViewSet.as_view({'get': 'list', 'post': 'create'}), name="EventList"),
        url(r'^event/(?P<pk>\d+)/$', EventViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='Event'),
        url(r'^event/all/$', EventViewSet.as_view({'get': 'list_all'}), name="EventListAll"),
        url(r'^event/feed/calendar/$', EventViewSet.as_view({'get': 'calendar_feed'}), name='EventCalendarFeed'),
        url(r'^event/feed/dashboard/$', EventViewSet.as_view({'get': 'dashboard_feed'}), name='EventDashboardFeed'),
]
