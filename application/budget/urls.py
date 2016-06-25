from django.conf.urls import url
from budget import views
from budget.views import OldBudgetViewSet, OldOtherItemsViewSet, OldStaffSalaryViewSet, MoneyDistribution, previous_data


other_items_list = OldOtherItemsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

other_items_detail = OldOtherItemsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

staff_salary_list = OldStaffSalaryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

staff_salary_detail = OldStaffSalaryViewSet.as_view({
    'get': 'budget_calc_retrieve',
    'put': 'update',
    'delete': 'destroy'
})

budget_detail_list = OldBudgetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

budget_detail = OldBudgetViewSet.as_view({
    'put': 'update',
    'get': 'retrieve',
    'delete': 'destroy'
})

distribution_detail = MoneyDistribution.as_view({
    'get': 'retrieve',
    'post': 'send_emails'
})

urlpatterns = [
    url(r'^budget_calculations/$', views.BudgetCalcListView.as_view(), name='budget_list'),
    url(r'^budget_calculations/delete/(?P<pk>\d+)/$', views.BudgetCalcDeleteView.as_view(), name='budget_delete'),

    url(r'^api/budget_calculations/$', budget_detail_list, name="budget_retrieve_list"),
    url(r'^api/budget_calculations/create/(?P<pk>\d+)/$', views.ng_budget_calc_create, name="budget_create_api"),
    url(r'^api/budget_calculations/update/(?P<pk>\d+)/$', views.ng_budget_calc_update, name="budget_update_api"),
    url(r'^api/budget_calculations/view/(?P<pk>\d+)/$', views.ng_budget_calc_view, name="budget_view_api"),
    url(r'^api/budget_calculations/(?P<pk>\d+)/$', budget_detail, name="budget_detail_api"),

    url(r'^api/budget_calculations/most_recent_form/(?P<pk>\d+)/$', views.retrieve_latest_budget_sheet_for_border_station, name="budget_new_api"),
    url(r'^api/budget_calculations/previous_data/(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', previous_data, name="previous_data"),

    url(r'^api/budget_calculations/items_list/$', other_items_list, name="other_items_list_api"),
    url(r'^api/budget_calculations/items_detail/(?P<pk>\d+)/$', other_items_detail, name="other_items_detail_api"),

    url(r'^api/budget_calculations/staff_salary/$', staff_salary_list, name="staff_salary_list_api"),
    url(r'^api/budget_calculations/staff_salary/(?P<pk>\d+)/$', staff_salary_detail, name="staff_salary_detail_api"),


    url(r'^api/budget_calculations/money_distribution/(?P<pk>\d+)/$', distribution_detail, name="money_distribution_api"),
    url(r'^budget_calculations/money_distribution_pdf/(?P<pk>\d+)/$', views.MoneyDistributionFormPDFView.as_view(), name="money_distribution_pdf"),
    url(r'^budget_calculations/money_distribution/view/(?P<pk>\d+)/$', views.money_distribution_view, name="money_distribution_view"),
]
