from django.conf.urls import patterns, url
from dataentry.views import *

urlpatterns = patterns('dataentry.views',
    url(r'^ifvs/$', InterceptionRecordListView.as_view(), name='interceptionrecord_list'),
)
