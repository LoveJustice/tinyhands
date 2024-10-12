from django.urls import re_path, path

from dataentry.views import Address2ViewSet, Address1ViewSet, GeoCodeAddress1APIView, GeoCodeAddress2APIView, InterceptionRecordViewSet, VictimInterviewViewSet, IntercepteeViewSet, VictimInterviewDetailViewSet, PhotoExporter, IrfCsvExportView, VifCsvExportView, InterceptionAlertViewSet, PermissionViewSet, UserLocationPermissionViewSet
from dataentry.views import PersonViewSet, MasterPersonViewSet, PendingMatchViewSet
from dataentry.views import SiteSettingsViewSet, GoogleMapKeyViewSet
from dataentry.views import CountryViewSet
from dataentry.views import RegionViewSet
from dataentry.views import AuditViewSet, AuditSampleViewSet
from dataentry.views import IDManagementViewSet, TraffickerCheckViewSet, IrfFormViewSet, CifFormViewSet, PvfFormViewSet, LfFormViewSet, SfFormViewSet, VdfFormViewSet, GospelVerificationViewSet
from dataentry.views import FormViewSet, FormTypeViewSet
from dataentry.views import MonthlyReportFormViewSet
from dataentry.views import IndicatorsViewSet
from dataentry.views import BorderStationFormViewSet
from dataentry.views import StationStatisticsViewSet
from legal.views import LegalChargeFormViewSet, LegalChargeCountrySpecificViewSet
from dataentry.views import ClientDiagnosticViewSet
from dataentry.views import EmpowermentViewSet
from dataentry.views import GospelViewSet
from dataentry.views import IncidentViewSet
from dataentry.views import MonitorAppViewSet
from dataentry.views import FormExportCsv
from help.views import VideoViewSet
from dataentry.views import auth0 as auth0_views

list = {'get': 'list', 'post': 'create'}
detail = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
    # Data Entry App
        # Addresses
        re_path(r'^address1/$', Address1ViewSet.as_view(list), name='Address1'),
        re_path(r'^address1/all/$', Address1ViewSet.as_view({'get': 'list_all'}), name='Address1all'),
        re_path(r'^address1/(?P<pk>\d+)/$', Address1ViewSet.as_view(detail), name='Address1detail'),
        re_path(r'^address1/(?P<pk>\d+)/related-items/$', Address1ViewSet.as_view({'get': 'related_items'}), name='Address1RelatedItems'),
        re_path(r'^address1/(?P<pk>\d+)/swap-with/(?P<pk2>\d+)/$', Address1ViewSet.as_view({'delete': 'swap_addresses'}), name='Address1RelatedItemsSwap'),

        re_path(r'^address2/$', Address2ViewSet.as_view(list), name='Address2'),
        re_path(r'^address2/(?P<pk>\d+)/$', Address2ViewSet.as_view(detail), name='Address2detail'),
        re_path(r'^address2/(?P<pk>\d+)/related-items/$', Address2ViewSet.as_view({'get': 'related_items'}), name='Address2RelatedItems'),
        re_path(r'^address2/(?P<pk>\d+)/swap-with/(?P<pk2>\d+)/$', Address2ViewSet.as_view({'delete': 'swap_addresses'}), name='Address2RelatedItemsSwap'),

        re_path(r'^address1/fuzzy/$', GeoCodeAddress1APIView.as_view(), name="Address1FuzzySearch"),
        re_path(r'^address2/fuzzy/$', GeoCodeAddress2APIView.as_view(), name="Address2FuzzySearch"),

        # IRFs
        re_path(r'^irf/$', InterceptionRecordViewSet.as_view(list), name="InterceptionRecord"),
        re_path(r'^irf/(?P<pk>\d+)/$', InterceptionRecordViewSet.as_view(detail), name="InterceptionRecordDetail"),
        re_path(r'^irf/export/$', IrfCsvExportView.as_view(), name="InterceptionRecordCsvExport"),

        # Interceptee
        re_path(r'^interceptee/$', IntercepteeViewSet.as_view(list), name="Interceptee"),
        re_path(r'^interceptee/(?P<pk>\d+)/$', IntercepteeViewSet.as_view(detail), name="IntercepteeDetail"),

        #SiteSettings
        re_path(r'^site-settings/$', SiteSettingsViewSet.as_view({'get': 'retrieve_custom'}), name="SiteSettings"),
        re_path(r'^site-settings/(?P<pk>\d+)/$', SiteSettingsViewSet.as_view({'put': 'update'}), name="SiteSettingsUpdate"),
        re_path(r'^site-settings/google_map_key/$', GoogleMapKeyViewSet.as_view({'get': 'retrieve_google_map_key'}), name="GoogleMapKey"),

        # VIFs
        re_path(r'^vif/$', VictimInterviewViewSet.as_view(list), name="VictimInterview"),
        re_path(r'^vif/(?P<pk>\d+)/$', VictimInterviewDetailViewSet.as_view(detail), name="VictimInterviewDetail"),
        re_path(r'^vif/export/$', VifCsvExportView.as_view(), name="VictimInterviewCsvExport"),

        #IRFBatch
        re_path(r'^photos/(?P<start_date>(\d+)-(\d+)-\d+)/(?P<end_date>\d+-\d+-\d+)/$', PhotoExporter.as_view({'get': 'export_photos'}), name="PhotoExporter"),
        re_path(r'^photos/(?P<start_date>(\d+)-(\d+)-\d+)/(?P<end_date>\d+-\d+-\d+)/count/$', PhotoExporter.as_view({'get': 'count_photos_in_date_range'}), name="PhotoExporterCount"),

        #Persons
        re_path(r'^person/$', PersonViewSet.as_view({'get': 'list'}), name="Person"),
        re_path(r'^person/(?P<pk>\d+)/$', PersonViewSet.as_view({'get': 'retrieve'}), name="PersonDetail"),
        re_path(r'^person/associated/(?P<station_id>\d+)/(?P<form_number>\w+)/$', PersonViewSet.as_view({'get': 'associated_persons'}), name="AssociatedPersons"),
        
         re_path(r'^master-person/$', MasterPersonViewSet.as_view({'get': 'list'}), name="MasterPerson"),
         re_path(r'^master-person/(?P<pk>\d+)/$', MasterPersonViewSet.as_view(detail), name='MasterPersonDetail'),
         re_path(r'^master-person/type/(?P<type_name>[^/]+)/$', MasterPersonViewSet.as_view({'get':'retrieve_type'}), name='MasterPersonType'),
         re_path(r'^master-person/pv-relations/(?P<id>\d+)/$', MasterPersonViewSet.as_view({'get':'retrieve_pv_relations'}), name='MasterPersonRelations'),
         re_path(r'^master-person/remove/(?P<id>\d+)/(?P<person_id>\d+)/$', MasterPersonViewSet.as_view({'put':'remove_person'}), name='MasterPersonRemove'),
         re_path(r'^master-person/match/(?P<id>\d+)/(?P<type_id>\d+)/$', MasterPersonViewSet.as_view({'get':'retrieve_matches'}), name='MasterPersonMatch'),
         re_path(r'^master-person/update-match/(?P<id>\d+)/$', MasterPersonViewSet.as_view({'put':'update_match'}), name='MasterPersonUpdateMatch'),
         re_path(r'^master-person/create-match/$', MasterPersonViewSet.as_view({'put':'create_match'}), name='MasterPersonCreateMatch'),
         re_path(r'^master-person/merge/(?P<id1>\d+)/(?P<id2>\d+)/$', MasterPersonViewSet.as_view({'put':'merge_master_persons'}), name='MasterPersonMerge'),
         re_path(r'^pending-match/$', PendingMatchViewSet.as_view({'get': 'list'}), name='PendingMatchList'),
         re_path(r'^pending-match/(?P<pk>\d+)/$', PendingMatchViewSet.as_view({'get': 'retrieve_by_person_match_id'}), name='PendingMatch'),

        #KnownPersons
        re_path(r'^idmgmt/$', IDManagementViewSet.as_view({'get': 'list'}), name="IDManagement"),
        re_path(r'^idmgmt/fuzzy/$', TraffickerCheckViewSet.as_view({'get':'fuzzy_match'}), name="IDManagementFuzzy"),
        re_path(r'^idmgmt/phone/$', TraffickerCheckViewSet.as_view({'get':'partial_phone'}), name="IDManagementPhone"),
        re_path(r'^idmgmt/aperson/$', IDManagementViewSet.as_view({'get':'get_person'}), name="IDManagementPerson"),
        re_path(r'^idmgmt/forms/$', IDManagementViewSet.as_view({'get':'person_forms'}), name="IDManagementForms"),
        re_path(r'^idmgmt/group/$', IDManagementViewSet.as_view({'get':'alias_group'}), name="IDManagementGroup"),
        re_path(r'^idmgmt/(?P<pk>\d+)/addgroup/(?P<pk2>\d+)/$', IDManagementViewSet.as_view({'put':'add_alias_group'}), name="IDManagementAdd"),
        re_path(r'^idmgmt/(?P<pk>\d+)/removegroup/$', IDManagementViewSet.as_view({'put':'remove_alias_group'}), name="IDManagementRemove"),

        re_path(r'^region/$', RegionViewSet.as_view(list), name='Region'),
        #Countries
        re_path(r'^country/$', CountryViewSet.as_view(list), name='Country'),
        re_path(r'^country/(?P<pk>\d+)/$', CountryViewSet.as_view(detail), name='Countrydetail'),
        
       re_path(r'^intercept-alerts/$', InterceptionAlertViewSet.as_view({'get':'list'}), name='InterceptionAlert'), 
       
       re_path(r'^permission/$', PermissionViewSet.as_view({'get':'list'}), name='Permission'),
       re_path(r'^user_permission_list/$', UserLocationPermissionViewSet.as_view({'get':'user_permission_list'}), name='UserLocationPermissionList'),
       re_path(r'^user_permission/(?P<pk>\d+)/$', UserLocationPermissionViewSet.as_view({'get':'user_permissions', 'put':'update_permissions'}), name='UserLocationPermission'),
       re_path(r'^user_permission/countries/(?P<pk>\d+)/$', UserLocationPermissionViewSet.as_view({'get':'user_countries'}), name='UserPermissionCountries'),
       re_path(r'^user_permission/countries/current-user/$', UserLocationPermissionViewSet.as_view({'get':'user_countries_current_user'}), name='UserPermissionCountriesCurrent'),
       re_path(r'^user_permission/stations/(?P<pk>\d+)/$', UserLocationPermissionViewSet.as_view({'get':'user_stations'}), name='UserPermissionStations'),
        
        re_path(r'^irfNew/$', IrfFormViewSet.as_view(list), name='irfNew'),
        re_path(r'^irfNew/(?P<station_id>\d+)/(?P<pk>\d+)', IrfFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='irfNewDetail'),
        re_path(r'^irfNew/blank/(?P<station_id>\d+)', IrfFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='irfNewBlank'),
        re_path(r'^irfNew/tally/$', IrfFormViewSet.as_view({'get': 'tally'}), name='irfNewTally'),
        re_path(r'^irfNew/six-month-tally/$', IrfFormViewSet.as_view({'get': 'six_month_tally'}), name='sixMonthTally'),
        re_path(r'^irfNew/attachments/(?P<start_date>(\d+)-(\d+)-\d+)/(?P<end_date>\d+-\d+-\d+)/$', IrfFormViewSet.as_view({'get': 'export_attachments'}), name="AttachmentExporter"),
        re_path(r'^irfNew/attachments/(?P<start_date>(\d+)-(\d+)-\d+)/(?P<end_date>\d+-\d+-\d+)/count/$', IrfFormViewSet.as_view({'get': 'count_attachments_in_date_range'}), name="AttachmentExporterCount"),
        
        
        re_path(r'^forms/$', FormViewSet.as_view({'get':'list'}), name='forns'),
        re_path(r'^forms/config/(?P<form_name>\w+)/$', FormViewSet.as_view({'get':'form_config'}), name='formConfig'),
        re_path(r'^forms/types/$', FormTypeViewSet.as_view({'get':'list'}), name='fornTypes'),
        re_path(r'^forms/(?P<station_id>\d+)/station_forms/$', FormViewSet.as_view({'put':'set_forms'}), name='setForms'),
        re_path(r'^forms/related/(?P<station_id>\d+)/(?P<form_number>[^/]+)/$', FormViewSet.as_view({'get':'related_forms'}), name='relatedForms'),
        re_path(r'^forms/countries/(?P<form_id>\d+)/$', FormViewSet.as_view({'get':'get_form_countries'}), name='formCountries'),
        re_path(r'^forms/versions/(?P<form_id>\d+)/(?P<country_id>\d+)/$', FormViewSet.as_view({'get':'get_form_versions'}), name='formVersions'),
        re_path(r'^forms/csv/$', FormExportCsv.as_view({'get':'export_csv'}), name='formCsv'),
        
        
        re_path(r'^cif/$', CifFormViewSet.as_view(list), name='cif'),
        re_path(r'^cif/(?P<station_id>\d+)/(?P<pk>\d+)', CifFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='cifDetail'),
        re_path(r'^cif/blank/(?P<station_id>\d+)', CifFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='cifBlank'),
        
        re_path(r'^vdf/$', VdfFormViewSet.as_view(list), name='vdf'),
        re_path(r'^vdf/(?P<station_id>\d+)/(?P<pk>\d+)', VdfFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='vdfDetail'),
        re_path(r'^vdf/blank/(?P<station_id>\d+)', VdfFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='vdfBlank'),
        re_path(r'^gospel-verification/$', GospelVerificationViewSet.as_view({'get': 'list'}), name='gospelVerificationList'),
        re_path(r'^gospel-verification/(?P<station_id>\d+)/(?P<pk>\d+)/$', GospelVerificationViewSet.as_view({'get': 'my_retrieve', 'put': 'update'}), name='gospelVerificationDetail'),
        re_path(r'^gospel-vdf-update/(?P<pk>\d+)/$', GospelVerificationViewSet.as_view({'put': 'update_vdf_gospel'}), name='gospelVdfUpdate'),
        re_path(r'^gospel-verification/vdf-number/(?P<station_id>\d+)/(?P<form_number>[^/]+)/$', GospelVerificationViewSet.as_view({'get': 'retrieve_by_form_number'}), name='gospelVerificationFormNumber'),
        re_path(r'^gospel-verification/pvf-number/(?P<station_id>\d+)/(?P<form_number>[^/]+)/$', GospelVerificationViewSet.as_view({'get': 'retrieve_by_form_number'}), name='gospelVerificationFormNumber2'),
        
        re_path(r'^pvf/$', PvfFormViewSet.as_view(list), name='pvf'),
        re_path(r'^pvf/(?P<station_id>\d+)/(?P<pk>\d+)', PvfFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='pvfDetail'),
        re_path(r'^pvf/blank/(?P<station_id>\d+)', PvfFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='pvfBlank'),
        
        re_path(r'^sf/$', SfFormViewSet.as_view(list), name='sf'),
        re_path(r'^sf/(?P<station_id>\d+)/(?P<pk>\d+)', SfFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='sfDetail'),
        re_path(r'^sf/blank/(?P<station_id>\d+)', SfFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='sfBlank'),
        re_path(r'^sf/associated/(?P<pk>\d+)', SfFormViewSet.as_view({'get': 'get_associated_incidents', 'put': 'set_associated_incidents'}), name='sfAssociated'),
        
        re_path(r'^lf/$', LfFormViewSet.as_view(list), name='lf'),
        re_path(r'^lf/(?P<station_id>\d+)/(?P<pk>\d+)', LfFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='lfDetail'),
        re_path(r'^lf/blank/(?P<station_id>\d+)', LfFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='lfBlank'),
        re_path(r'^lf/associated/(?P<pk>\d+)', LfFormViewSet.as_view({'get': 'get_associated_incidents', 'put': 'set_associated_incidents'}), name='lfAssociated'),
        
        re_path(r'^monthly_report/$', MonthlyReportFormViewSet.as_view(list), name='monthlyReport'),
        re_path(r'^monthly_report/(?P<station_id>\d+)/(?P<pk>\d+)', MonthlyReportFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='monthlyReportDetail'),
        re_path(r'^monthly_report/blank/(?P<station_id>\d+)', MonthlyReportFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='monthlyReportBlank'),
        re_path(r'^monthly_report/summary/(?P<country_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/$', MonthlyReportFormViewSet.as_view({'get': 'summary'}), name='monthlyReportSummary'),
        
        re_path(r'^indicators/(?P<country_id>\d+)$', IndicatorsViewSet.as_view({'get': 'calculate_indicators'}), name='indicators'),
        re_path(r'^collection_indicators/(?P<country_id>\d+)/$', IndicatorsViewSet.as_view({'get': 'get_collection_indicators'}), name='collectionIndicators'),
        re_path(r'^collection_indicators/detail/$', IndicatorsViewSet.as_view({'get': 'collection_details'}), name='collectionDetails'),
        
        re_path(r'help/video/$', VideoViewSet.as_view({'get':'list'}), name='helpVideo'),
        
        re_path(r'^border_station/$', BorderStationFormViewSet.as_view({'post': 'create'}), name="borderStation"),
        re_path(r'^border_station/(?P<pk>\d+)/$', BorderStationFormViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name="borderStationForm"),
        re_path(r'^border_station/blank/', BorderStationFormViewSet.as_view({'get': 'retrieve_blank'}), name='borderStationBlank'),
        re_path(r'^border_station/category/', BorderStationFormViewSet.as_view({'get': 'get_project_categories'}), name='borderStationCategory'),
        
        re_path(r'^operations-dashboard/(?P<country_id>\d+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_dashboard'}), name='retrieveDashboard'),
        re_path(r'^station-data/detail/(?P<station_id>\d+)/(?P<year_month>\d+)/(?P<data_type>\w+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_detail'}), name='retrieveStationDetails'),
        re_path(r'^station-data/country/(?P<country_id>\d+)/(?P<year_month>\d+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_country_data'}), name='retrieveCountryOperations'),
        re_path(r'^station-data/country/$', StationStatisticsViewSet.as_view({'put': 'update_station_data'}), name='setCountryOperations'),
        re_path(r'^location-staff/(?P<station_id>\d+)/(?P<year_month>\d+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_location_staff'}), name='retrieveLocationStaff'),
        re_path(r'^location-staff-staff/(?P<station_id>\d+)/(?P<year_month>\d+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_location_staff_staff'}), name='retrieveLocationStaffStaff'),
        re_path(r'^location-staff/$', StationStatisticsViewSet.as_view({'put': 'update_location_staff'}), name='setLocationStaff'),
        re_path(r'^location-statistics/(?P<station_id>\d+)/(?P<year_month>\d+)/$', StationStatisticsViewSet.as_view({'get': 'retrieve_location_statistics'}), name='retrieveLocationStatistics'),
        re_path(r'^location-statistics/$', StationStatisticsViewSet.as_view({'put': 'update_location_statistics'}), name='setLocationStatistics'),
        re_path(r'^exchange-rate/(?P<country_id>\d+)/(?P<year_month>\d+)/$', StationStatisticsViewSet.as_view({'get': 'get_exchange_rate'}), name='getExchangeRate'),
        re_path(r'^exchange-rate/$', StationStatisticsViewSet.as_view({'put': 'update_exchange_rate'}), name='updateExchangeRate'),
        
        #Audits
        re_path(r'^audit/$', AuditViewSet.as_view(list), name='Audit'),
        re_path(r'^audit/(?P<pk>\d+)/$', AuditViewSet.as_view(detail), name='Auditdetail'),
        re_path(r'^audit/sample-size/$', AuditViewSet.as_view({'get':'sample_size'}), name='Auditdetail'),
        re_path(r'^audit-notes/(?P<pk>\d+)/$', AuditViewSet.as_view({'put':'update_notes'}), name='AuditNotes'),
        re_path(r'^audit-sample/$', AuditSampleViewSet.as_view(list), name='Audit'),
        re_path(r'^audit-sample/(?P<pk>\d+)/$', AuditSampleViewSet.as_view(detail), name='Auditdetail'),

        re_path(r'^legal-charge/$', LegalChargeFormViewSet.as_view(list), name='legalCharge'),
        re_path(r'^legal-charge/(?P<station_id>\d+)/(?P<pk>\d+)', LegalChargeFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update', 'delete': 'destroy'}), name='legalChargeDetail'),
        re_path(r'^legal-charge/blank/(?P<station_id>\d+)', LegalChargeFormViewSet.as_view({'get': 'retrieve_blank_form'}), name='legalChargeBlank'),
        re_path(r'^legal-charge/incident/(?P<pk>\d+)', LegalChargeFormViewSet.as_view({'get': 'get_incident_detail'}), name='legalChargeIncident'),
        
        re_path(r'^legal-charge/country-specific/', LegalChargeCountrySpecificViewSet.as_view({'get': 'list'}), name='legalChargeCountrySpecific'),
        
        re_path(r'^emp/$', EmpowermentViewSet.as_view(list), name='Empowerment'),
        re_path(r'^emp/(?P<pk>\d+)/$', EmpowermentViewSet.as_view(detail), name='EmpowermentDetail'),
        re_path(r'^emp/blank/(?P<station_id>\d+)/$', EmpowermentViewSet.as_view({'get': 'retrieve_blank'}), name='EmpowermentBlank'),
        
        re_path(r'^gsp/$', GospelViewSet.as_view(list), name='Gospel'),
        re_path(r'^gsp/(?P<pk>\d+)/$', GospelViewSet.as_view(detail), name='Gospeldetail'),
        re_path(r'^gsp/blank/(?P<station_id>\d+)/$', GospelViewSet.as_view({'get': 'retrieve_blank'}), name='GospelBlank'),
        
        re_path(r'^incident/$', IncidentViewSet.as_view(list), name='Incident'),
        re_path(r'^incident/(?P<pk>\d+)/$', IncidentViewSet.as_view(detail), name='Incidentdetail'),
        re_path(r'^incident/names/$', IncidentViewSet.as_view({'get':'get_names_and_addresses'}), name='IncidentNames'),
        
        re_path(r'^diagnostic/$', ClientDiagnosticViewSet.as_view(list), name='Diagnostic'),
        re_path(r'^monitor-form/$', MonitorAppViewSet.as_view({'post':'create'}), name='MonitorApp'),

        re_path(r'^auth0/send-me-password-reset-email$', auth0_views.send_current_user_password_reset_email),
        path('auth0/update-user/<str:username>', auth0_views.update_auth0_user_view),
]
