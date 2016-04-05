from django.conf.urls import url
from static_border_stations.views import *

staff_detail = StaffViewSet.as_view({
    'get': 'staff_retrieve',
    'post': 'create',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'^border-stations/create/$', StaticBorderStationsCreateView.as_view() , name='borderstations_create'),
    url(r'^border-stations/update/(?P<pk>\d+)/$', StaticBorderStationsUpdateView.as_view(), name='borderstations_update'),
    url(r'^border-stations/(?P<pk>\d+)/$', StaticBorderStationsDetailView.as_view(), name='borderstations_view'),
    url(r'^api/border-stations/(?P<pk>\d+)/$', staff_detail, name="staff_detail_api")
]
