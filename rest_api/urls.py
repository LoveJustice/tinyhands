from django.conf.urls import patterns, url

from dataentry.views import Address2ViewSet
from budget.views import BudgetViewSet, OtherItemsViewSet

urlpatterns = patterns('rest_api.views',
    # Budget URLs
    url(r'^budgetcalculationform/$', BudgetViewSet.as_view({'get': 'list', 'post': 'create'}), name='BudgetCalculation'),
    url(r'^budgetcalculationform/(?P<pk>\d+)/$', BudgetViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='BudgetCalculationWithId'),

    # Other items
    url(r'^budgetcalculationform/(?P<parent_pk>\d+)/otheritem/$', OtherItemsViewSet.as_view({'get': 'list_by_budget_sheet', 'post': 'create'}), name='BudgetCalculationWithId'),
    url(r'^budgetcalculationform/(?P<parent_pk>\d+)/otheritem/(?P<pk>\d+)/$', OtherItemsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='BudgetCalculationWithId'),


    # Address 2s
    url(r'^address2/$', Address2ViewSet.as_view({'get': 'list', 'post': 'create'}), name='Address2'),
    url(r'^address2/(?P<pk>\d+)/$', Address2ViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='Address2detail'),
    url(r'^address2/search/(?P<search_value>[\w]+)/$', Address2ViewSet.as_view({'get': 'search'}), name='Address2Search'),

)
