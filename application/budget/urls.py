from django.conf.urls import url
from budget.views import \
    BudgetViewSet, \
    OtherItemsViewSet, \
    MoneyDistribution, \
    MoneyDistributionFormPDFView, \
    budget_sheet_by_date, \
    StaffSalaryViewSet, \
    get_top_table_data

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
        url(r'^budget/$', BudgetViewSet.as_view(list_methods), name='BudgetCalculation'),
        url(r'^budget/(?P<pk>\d+)/$', BudgetViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),
        url(r'^budget/(?P<pk>\d+)/top_table_data/$', get_top_table_data, name='get_top_table_data'),

        url(r'^budget/(?P<parent_pk>\d+)/item/$', OtherItemsViewSet.as_view(list_methods), name='BudgetCalculationWithId'),
        url(r'^budget/(?P<parent_pk>\d+)/item/(?P<pk>\d+)/$', OtherItemsViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),

        url(r'^budget/(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', budget_sheet_by_date, name="rest_api_budget_sheet_by_date"),

        url(r'^budget/staff_salary/$', StaffSalaryViewSet.as_view(list_methods), name="rest_api_staff_salary_list_api"),
        url(r'^budget/(?P<parent_pk>\d+)/staff_salary/$', StaffSalaryViewSet.as_view({'get': 'budget_calc_retrieve'}), name="rest_api_staff_salary_detail_api"),
        url(r'^budget/(?P<parent_pk>\d+)/staff_salary/(?P<pk>\d+)/$', StaffSalaryViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name="rest_api_staff_salary_detail_api"),

        url(r'^mdf/(?P<pk>\d+)/$', MoneyDistribution.as_view({'get': 'retrieve', 'post': 'send_emails'}), name="MDFViewSet"),
        url(r'^mdf/(?P<uuid>[0-9A-Fa-f-]+)/pdf/$', MoneyDistributionFormPDFView.as_view(), name="MdfPdf"),
]
