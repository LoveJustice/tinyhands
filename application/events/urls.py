from django.conf.urls import patterns, url

from events.views import EventJson, EventCalendarView, EventListView, EventCreateView, EventDeleteView, EventUpdateView

urlpatterns = patterns('dataentry.views',
    url(r'^create/$', EventCreateView.as_view(), name='create_event'),
    url(r'^update/(?P<pk>[0-9]+)/$', EventUpdateView.as_view(), name='update_event'),
    url(r'^delete/(?P<pk>[0-9]+)/$', EventDeleteView.as_view(), name='delete_event'),
    url(r'^list/$', EventListView.as_view(), name='list_event'),
    url(r'^calendar/$', EventCalendarView.as_view(), name='event_calendar'),
    url(r'^list.json/$', EventJson.as_view(), name='event_list_json'),
    url(r'^list.json/(?P<dashboard>dashboard)/$', EventJson.as_view(), name='event_list_dashboard'),
)
