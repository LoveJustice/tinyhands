from django.conf.urls import patterns, url
from portal.views import *

urlpatterns = patterns('portal.views',
    url(r'^dashboard/$', main_dashboard, name='main_dashboard'),
    url(r'^get_border_stations/$', get_border_stations, name='get_border_stations'),
    url(r'^get_interception_records/$', get_interception_records, name='get_interception_records'),
    url(r'^tally/days/$', TallyDaysView.as_view(), name='tally_day_api'),
)
