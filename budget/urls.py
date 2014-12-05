from django.conf.urls import patterns, url
from budget import views


urlpatterns = patterns('portal.views',
    url(r'^budget_calculations/$', views.BudgetCalcListView.as_view(), name='budget_list'),
    url(r'^budget_calculations/create/(?P<pk>\d+)$', views.budget_calc_create, name='budget_create'),
    url(r'^budget_calculations/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_detail'),
    url(r'^budget_calculations/update/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_update'),
    url(r'^budget_calculations/delete/(?P<pk>\d+)/$', views.BudgetCalcDeleteView.as_view(), name='budget_delete'),
)
