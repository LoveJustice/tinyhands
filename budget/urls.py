from django.conf.urls import patterns, url
from budget import views
from budget.views import BudgetViewSet, OtherItemsViewSet, StaffSalaryViewSet

other_items_list = OtherItemsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

other_items_detail = OtherItemsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

staff_salary_list = StaffSalaryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

staff_salary_detail = StaffSalaryViewSet.as_view({
    'get': 'budget_calc_retrieve',
    'put': 'update',
    'delete': 'destroy'
})

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

    url(r'^api/budget_calculations/most_recent_form/(?P<pk>\d+)/$', views.retrieve_latest_budget_sheet_for_border_station, name="budget_new_api"),

    url(r'^api/budget_calculations/items_list/$', other_items_list, name="other_items_list_api"),
    url(r'^api/budget_calculations/items_detail/(?P<pk>\d+)/$', other_items_detail, name="other_items_detail_api"),

    url(r'^api/budget_calculations/staff_salary/$', staff_salary_list, name="staff_salary_list_api"),
    url(r'^api/budget_calculations/staff_salary/(?P<pk>\d+)/$', staff_salary_detail, name="staff_salary_detail_api"),
)




