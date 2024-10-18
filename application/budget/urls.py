from django.urls import re_path
from budget.views import \
    BudgetViewSet, \
    StaffBudgetItemViewSet, \
    OtherItemsViewSet, \
    MoneyDistribution, \
    MDFExportViewSet, \
    budget_sheet_by_date, \
    get_top_table_data, \
    ProjectRequestViewSet, \
    ProjectRequestDiscussionViewSet, \
    ProjectRequestAttachmentViewSet, \
    MdfCombinedViewSet, \
    MonthlyDistributionFormViewSet, \
    MdfItemViewSet

list_methods = {'get': 'list', 'post': 'create'}
detail_methods = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
        re_path(r'^budget/$', BudgetViewSet.as_view(list_methods), name='BudgetCalculation'),
        re_path(r'^budget/(?P<pk>\d+)/$', BudgetViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),
        re_path(r'^budget/(?P<pk>\d+)/top_table_data/$', get_top_table_data, name='get_top_table_data'),
        re_path(r'^budget/(?P<pk>\d+)/finalize/$', BudgetViewSet.as_view({'put':'finalize'}), name='BudgetFinalize'),

        re_path(r'^budget/(?P<parent_pk>\d+)/item/$', OtherItemsViewSet.as_view(list_methods), name='BudgetCalculationWithId'),
        re_path(r'^budget/(?P<parent_pk>\d+)/item/(?P<pk>\d+)/$', OtherItemsViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),

        re_path(r'^budget/(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', budget_sheet_by_date, name="rest_api_budget_sheet_by_date"),

        re_path(r'^budget/staff_item/$', StaffBudgetItemViewSet.as_view(list_methods), name="rest_api_staff_item_list_api"),
        re_path(r'^budget/(?P<parent_pk>\d+)/staff_item/$', StaffBudgetItemViewSet.as_view({'get': 'budget_calc_retrieve'}), name="rest_api_staff_item_detail_api"),
        re_path(r'^budget/(?P<parent_pk>\d+)/staff_item/(?P<pk>\d+)/$', StaffBudgetItemViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name="rest_api_staff_item_detail_api"),

        re_path(r'^mdf/(?P<pk>\d+)/$', MoneyDistribution.as_view({'get': 'retrieve', 'post': 'send_emails'}), name="MDFViewSet"),
        re_path(r'^mdf/(?P<uuid>[0-9A-Fa-f-]+)/(?P<mdf_type>[a-z-]+)/pdf/$', MDFExportViewSet.as_view({'get': 'get_mdf_pdf'}, permission_classes=[]), name="MdfPdf"),
        re_path(r'^mdf/(?P<month>\d+)/(?P<year>\d+)/(?P<country_id>\d+)/pdf/$', MDFExportViewSet.as_view({'get': 'get_mdf_pdf_bulk'}), name="MdfPdfbulk"),
        re_path(r'^mdf/(?P<month>\d+)/(?P<year>\d+)/(?P<country_id>\d+)/count/$', MDFExportViewSet.as_view({'get': 'count_mdfs_for_month_year'}), name="MdfPdfbulkCount"),
        
        re_path(r'^project-request/$', ProjectRequestViewSet.as_view(list_methods), name='ProjectRequest'),
        re_path(r'^project-request/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view(detail_methods), name='ProjectRequestWithId'),
        re_path(r'^project-request/category/(?P<project_id>\-?\d+)/$', ProjectRequestViewSet.as_view({'get': 'get_category_types'}), name='ProjectRequestCategory'),
        re_path(r'^project-request/benefits/(?P<project_id>\d+)/$', ProjectRequestViewSet.as_view({'get': 'get_benefit_types'}), name='ProjectRequestBenefits'),
        re_path(r'^project-request/multipliers/$', ProjectRequestViewSet.as_view({'get': 'get_multipliers'}), name='ProjectRequestMultipliers'),
        re_path(r'^project-request/approve/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view({'put': 'approve'}), name='ProjectRequestApprove'),
        re_path(r'^project-request/discussion-status/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view({'put':'update_discussion_status'}), name='ProjectDiscussionStatus'),
        
        re_path(r'^project-request/discussion/$', ProjectRequestDiscussionViewSet.as_view(list_methods), name='ProjectDiscussion'),
        re_path(r'^project-request/discussion/(?P<pk>\d+)/$', ProjectRequestDiscussionViewSet.as_view({'put':'update'}), name='ProjectDiscussionDetail'),
        re_path(r'^project-request/account/(?P<id>\d+)/$', ProjectRequestDiscussionViewSet.as_view({'get':'get_notify_accounts'}), name='ProjectAccount'),
        
        re_path(r'^project-request/attachment/$', ProjectRequestAttachmentViewSet.as_view(list_methods), name='ProjectRequestAttachment'),
        re_path(r'^project-request/attachment/(?P<pk>\d+)/$', ProjectRequestAttachmentViewSet.as_view({'delete':'destroy'}), name='ProjectRequestAttachmentDelete'),
        
        re_path(r'^mdf-combined/$', MdfCombinedViewSet.as_view({'get': 'list'}), name="MDFCombinedViewSet"),
        re_path(r'^mdf-pr/$', MonthlyDistributionFormViewSet.as_view({'get': 'list'}), name="MdfPRViewSet"),
        re_path(r'^mdf-pr/(?P<pk>\d+)/$', MonthlyDistributionFormViewSet.as_view(detail_methods), name="MdfPRViewSetDetail"),
        re_path(r'^mdf-pr/new/(?P<station_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', MonthlyDistributionFormViewSet.as_view({'get':'get_new_mdf'}), name="MdfPRViewSet"),
        re_path(r'^mdf-pr/approve/(?P<pk>\d+)/$', MonthlyDistributionFormViewSet.as_view({'put': 'approve_mdf'}), name="MdfPRViewSetApprove"),
        re_path(r'^mdf-pr/last-date/(?P<station_id>\d+)/$', MonthlyDistributionFormViewSet.as_view({'get': 'get_last_mdf_date'}), name="MdfPRViewSetApprove"),
        re_path(r'^mdf-pr/trend/(?P<pk>\d+)/$', MonthlyDistributionFormViewSet.as_view({'get': 'get_trend'}), name="MdfPRViewSetTrend"),
        
        
        re_path(r'^mdf-item/$', MdfItemViewSet.as_view(list_methods), name='MdfItem'),
        re_path(r'^mdf-item/(?P<pk>\d+)/$', MdfItemViewSet.as_view(detail_methods), name='MdfItemDetail'),
]
