from django.urls import re_path
from portal.views import TallyDaysView

urlpatterns = [
    re_path(r'^portal/tally/days/$', TallyDaysView.as_view(), name='tally_day_api'),
]
