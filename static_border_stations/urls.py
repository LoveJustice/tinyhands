from django.conf.urls import patterns, url
from static_border_stations.views import *

urlpatterns = patterns('static_border_stations.views',
    url(r'^border-stations/create/$', StaticBorderStationsCreateView.as_view() , name='borderstations_create'),
    url(r'^border-stations/update/(?P<pk>\d+)/$', StaticBorderStationsUpdateView.as_view(), name='borderstations_update'),
)