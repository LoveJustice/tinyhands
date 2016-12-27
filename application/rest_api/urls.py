from django.conf.urls import url

from dataentry.views import Address2ViewSet, Address1ViewSet, GeoCodeAddress1APIView, GeoCodeAddress2APIView, InterceptionRecordViewSet, VictimInterviewViewSet, IntercepteeViewSet, VictimInterviewDetailViewSet, PhotoExporter, IrfCsvExportView, VifCsvExportView
from dataentry.views import PersonViewSet
from dataentry.views import SiteSettingsViewSet


list = {'get': 'list', 'post': 'create'}
detail = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
    # Data Entry App
        # Addresses
        url(r'^address1/$', Address1ViewSet.as_view(list), name='Address1'),
        url(r'^address1/all/$', Address1ViewSet.as_view({'get': 'list_all'}), name='Address1all'),
        url(r'^address1/(?P<pk>\d+)/$', Address1ViewSet.as_view(detail), name='Address1detail'),
        url(r'^address1/(?P<pk>\d+)/related-items/$', Address1ViewSet.as_view({'get': 'related_items'}), name='Address1RelatedItems'),
        url(r'^address1/(?P<pk>\d+)/swap-with/(?P<pk2>\d+)/$', Address1ViewSet.as_view({'get': 'swap_addresses'}), name='Address1RelatedItemsSwap'),

        url(r'^address2/$', Address2ViewSet.as_view(list), name='Address2'),
        url(r'^address2/(?P<pk>\d+)/$', Address2ViewSet.as_view(detail), name='Address2detail'),
        url(r'^address2/(?P<pk>\d+)/related-items/$', Address2ViewSet.as_view({'get': 'related_items'}), name='Address2RelatedItems'),

        url(r'^address1/fuzzy/$', GeoCodeAddress1APIView.as_view(), name="Address1FuzzySearch"),
        url(r'^address2/fuzzy/$', GeoCodeAddress2APIView.as_view(), name="Address2FuzzySearch"),

        # IRFs
        url(r'^irf/$', InterceptionRecordViewSet.as_view(list), name="InterceptionRecord"),
        url(r'^irf/(?P<pk>\d+)/$', InterceptionRecordViewSet.as_view(detail), name="InterceptionRecordDetail"),
        url(r'^irf/export/$', IrfCsvExportView.as_view(), name="InterceptionRecordCsvExport"),

        # Interceptee
        url(r'^interceptee/$', IntercepteeViewSet.as_view(list), name="Interceptee"),
        url(r'^interceptee/(?P<pk>\d+)/$', IntercepteeViewSet.as_view(detail), name="IntercepteeDetail"),

        #SiteSettings
        url(r'^site-settings/$', SiteSettingsViewSet.as_view({'get': 'retrieve_custom'}), name="SiteSettings"),
        url(r'^site-settings/(?P<pk>\d+)/$', SiteSettingsViewSet.as_view({'put': 'update'}), name="SiteSettingsUpdate"),

        # VIFs
        url(r'^vif/$', VictimInterviewViewSet.as_view(list), name="VictimInterview"),
        url(r'^vif/(?P<pk>\d+)/$', VictimInterviewDetailViewSet.as_view(detail), name="VictimInterviewDetail"),
        url(r'^vif/export/$', VifCsvExportView.as_view(), name="VictimInterviewCsvExport"),

        #IRFBatch
        url(r'^photos/(?P<startDate>(\d+)-(\d+)-\d+)/(?P<endDate>\d+-\d+-\d+)/$', PhotoExporter.as_view({'get': 'export_photos'}), name="PhotoExporter"),
        url(r'^photos/(?P<startDate>(\d+)-(\d+)-\d+)/(?P<endDate>\d+-\d+-\d+)/count/$', PhotoExporter.as_view({'get': 'count_photos_in_date_range'}), name="PhotoExporterCount"),

        #Persons
        url(r'^person/$', PersonViewSet.as_view({'get': 'list'}), name="Person"),
]
