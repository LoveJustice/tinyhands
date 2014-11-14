from django.conf.urls import patterns, url
from budget import views

urlpatterns = patterns('portal.views',
    url(r'^budget_calculation/$', views.BudgetCalcCreateView.as_view(), name='budget_create'),
)