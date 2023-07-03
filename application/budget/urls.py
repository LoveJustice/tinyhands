from django.conf.urls import url
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
        url(r'^budget/$', BudgetViewSet.as_view(list_methods), name='BudgetCalculation'),
        url(r'^budget/(?P<pk>\d+)/$', BudgetViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),
        url(r'^budget/(?P<pk>\d+)/top_table_data/$', get_top_table_data, name='get_top_table_data'),
        url(r'^budget/(?P<pk>\d+)/finalize/$', BudgetViewSet.as_view({'put':'finalize'}), name='BudgetFinalize'),

        url(r'^budget/(?P<parent_pk>\d+)/item/$', OtherItemsViewSet.as_view(list_methods), name='BudgetCalculationWithId'),
        url(r'^budget/(?P<parent_pk>\d+)/item/(?P<pk>\d+)/$', OtherItemsViewSet.as_view(detail_methods), name='BudgetCalculationWithId'),

        url(r'^budget/(?P<pk>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', budget_sheet_by_date, name="rest_api_budget_sheet_by_date"),

        url(r'^budget/staff_item/$', StaffBudgetItemViewSet.as_view(list_methods), name="rest_api_staff_item_list_api"),
        url(r'^budget/(?P<parent_pk>\d+)/staff_item/$', StaffBudgetItemViewSet.as_view({'get': 'budget_calc_retrieve'}), name="rest_api_staff_item_detail_api"),
        url(r'^budget/(?P<parent_pk>\d+)/staff_item/(?P<pk>\d+)/$', StaffBudgetItemViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name="rest_api_staff_item_detail_api"),

        url(r'^mdf/(?P<pk>\d+)/$', MoneyDistribution.as_view({'get': 'retrieve', 'post': 'send_emails'}), name="MDFViewSet"),
        url(r'^mdf/(?P<uuid>[0-9A-Fa-f-]+)/pdf/$', MDFExportViewSet.as_view({'get': 'get_mdf_pdf'}, permission_classes=[]), name="MdfPdf"),
        url(r'^mdf/(?P<month>\d+)/(?P<year>\d+)/(?P<country_id>\d+)/pdf/$', MDFExportViewSet.as_view({'get': 'get_mdf_pdf_bulk'}), name="MdfPdfbulk"),
        url(r'^mdf/(?P<month>\d+)/(?P<year>\d+)/(?P<country_id>\d+)/count/$', MDFExportViewSet.as_view({'get': 'count_mdfs_for_month_year'}), name="MdfPdfbulkCount"),
        
        url(r'^project-request/$', ProjectRequestViewSet.as_view(list_methods), name='ProjectRequest'),
        url(r'^project-request/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view(detail_methods), name='ProjectRequestWithId'),
        url(r'^project-request/category/(?P<project_id>\d+)/$', ProjectRequestViewSet.as_view({'get': 'get_category_types'}), name='ProjectRequestCategory'),
        url(r'^project-request/benefits/(?P<project_id>\d+)/$', ProjectRequestViewSet.as_view({'get': 'get_benefit_types'}), name='ProjectRequestBenefits'),
        url(r'^project-request/multipliers/$', ProjectRequestViewSet.as_view({'get': 'get_multipliers'}), name='ProjectRequestMultipliers'),
        url(r'^project-request/approve/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view({'put': 'approve'}), name='ProjectRequestApprove'),
        url(r'^project-request/discussion-status/(?P<pk>\d+)/$', ProjectRequestViewSet.as_view({'put':'update_discussion_status'}), name='ProjectDiscussionStatus'),
        
        url(r'^project-request/discussion/$', ProjectRequestDiscussionViewSet.as_view(list_methods), name='ProjectDiscussion'),
        url(r'^project-request/account/(?P<id>\d+)/$', ProjectRequestDiscussionViewSet.as_view({'get':'get_notify_accounts'}), name='ProjectAccount'),
        
        url(r'^project-request/attachment/$', ProjectRequestAttachmentViewSet.as_view(list_methods), name='ProjectRequestAttachment'),
        url(r'^project-request/attachment/(?P<pk>\d+)/$', ProjectRequestAttachmentViewSet.as_view({'delete':'destroy'}), name='ProjectRequestAttachmentDelete'),
        
        url(r'^mdf-combined/$', MdfCombinedViewSet.as_view({'get': 'list'}), name="MDFCombinedViewSet"),
        url(r'^mdf-pr/$', MonthlyDistributionFormViewSet.as_view({'get': 'list'}), name="MdfPRViewSet"),
        url(r'^mdf-pr/(?P<pk>\d+)/$', MonthlyDistributionFormViewSet.as_view(detail_methods), name="MdfPRViewSetDetail"),
        url(r'^mdf-pr/new/(?P<station_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', MonthlyDistributionFormViewSet.as_view({'get':'get_new_mdf'}), name="MdfPRViewSet"),
        
        url(r'^mdf-item/$', MdfItemViewSet.as_view(list_methods), name='MdfItem'),
        url(r'^mdf-item/(?P<pk>\d+)/$', MdfItemViewSet.as_view(detail_methods), name='MdfItemDetail'),
]
