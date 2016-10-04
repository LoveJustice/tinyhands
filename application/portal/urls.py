from django.conf.urls import url
from portal.views import TallyDaysView

urlpatterns = [
    url(r'^portal/tally/days/$', TallyDaysView.as_view(), name='tally_day_api'),
]
