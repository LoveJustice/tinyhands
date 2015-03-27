from django.conf.urls import patterns, url
from budget import views
from rest_framework.routers import DefaultRouter
from budget.views import BudgetViewSet


budget_detail_list = BudgetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

budget_detail = BudgetViewSet.as_view({
    'put': 'update',
    'get': 'retrieve',
    'delete': 'destroy'
})

urlpatterns = patterns('budget.views',
    url(r'^budget_calculations/$', views.BudgetCalcListView.as_view(), name='budget_list'),
    url(r'^budget_calculations/delete/(?P<pk>\d+)/$', views.BudgetCalcDeleteView.as_view(), name='budget_delete'),
    # url(r'^budget_calculations/create/(?P<pk>\d+)/$', views.budget_calc_create, name='budget_create'),
    # url(r'^budget_calculations/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_detail'),
    # url(r'^budget_calculations/update/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_update'),
    url(r'^api/budget_calculations/$', budget_detail_list, name="budget_retrieve_list"),
    url(r'^api/budget_calculations/create/(?P<pk>\d+)/$', views.ng_budget_calc_create, name="budget_create_api"),
    url(r'^api/budget_calculations/update/(?P<pk>\d+)/$', views.ng_budget_calc_update, name="budget_update_api"),
    url(r'^api/budget_calculations/view/(?P<pk>\d+)/$', views.ng_budget_calc_view, name="budget_view_api"),
    url(r'^api/budget_calculations/(?P<pk>\d+)/$', budget_detail, name="budget_detail_api"),
)




