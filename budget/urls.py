from django.conf.urls import patterns, url
from budget import views
from rest_framework.routers import DefaultRouter
from budget.views import BudgetViewSet


budget_detail = BudgetViewSet.as_view({
    'get': 'retrieve'
})

budget_detail_list = BudgetViewSet.as_view({
    'get': 'list'
})

budget_create = BudgetViewSet.as_view({
    'post': 'create'
})

urlpatterns = patterns('budget.views',
    url(r'^budget_calculations/$', views.BudgetCalcListView.as_view(), name='budget_list'),
    url(r'^budget_calculations/create/(?P<pk>\d+)/$', views.budget_calc_create, name='budget_create'),
    url(r'^budget_calculations/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_detail'),
    url(r'^budget_calculations/update/(?P<pk>\d+)/$', views.budget_calc_update, name='budget_update'),
    url(r'^budget_calculations/delete/(?P<pk>\d+)/$', views.BudgetCalcDeleteView.as_view(), name='budget_delete'),
    url(r'^api/budget_calculations/$', budget_detail_list, name="budget_retrieve_list"),
    url(r'^api/budget_calculations/(?P<pk>\d+)/$', budget_detail, name="budget_retrieve"),
    url(r'^api/budget_calculations/create/(?P<pk>\d+)/$', budget_create, name="budget_create_api"),
)




