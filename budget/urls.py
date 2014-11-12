from django.conf.urls import patterns, url
from budget.views import *

urlpatterns = patterns('portal.views',
    url(r'^budget_calculation/$', budget_create, name='budget_create'),
)