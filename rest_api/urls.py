from django.conf.urls import patterns, url
from budget.views import BudgetViewSet, OtherItemsViewSet
from static_border_stations.views import BorderStationViewSet, StaffViewSet

urlpatterns = patterns('rest_api.views',
    # Budget URLs
    url(r'^budgetcalculationform/$', BudgetViewSet.as_view({'get': 'list', 'post': 'create'}), name='BudgetCalculation'),
    url(r'^budgetcalculationform/(?P<pk>\d+)/$', BudgetViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='BudgetCalculationWithId'),

    url(r'^otheritem/$', OtherItemsViewSet.as_view({'get': 'list'}), name='OtherItemsList'),
    url(r'^budgetcalculationform/(?P<parent_pk>\d+)/otheritem/$', OtherItemsViewSet.as_view({'get': 'list_by_budget_sheet', 'post': 'create'}), name='BudgetCalculationWithId'),
    url(r'^budgetcalculationform/(?P<parent_pk>\d+)/otheritem/(?P<pk>\d+)/$', OtherItemsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='BudgetCalculationWithId'),


    # BorderStation URLs
    url(r'^border-stations/$', BorderStationViewSet.as_view({'get':'list', 'post':'create'}), name="BorderStations"), # Detail
    url(r'^border-stations/(?P<pk>\d+)/$', BorderStationViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="BorderStation"),

    # Staff
    url(r'^staff/$', StaffViewSet.as_view({'get':'list', 'post':'create'}), name="BorderStations"), # Detail
    url(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="BorderStation"),
)
