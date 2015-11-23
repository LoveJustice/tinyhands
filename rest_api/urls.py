from django.conf.urls import patterns, url
from accounts.views import CurrentUserView

from rest_framework.authtoken import views

from budget.views import BudgetViewSet, OtherItemsViewSet
from dataentry.views import Address2ViewSet, Address1ViewSet, GeoCodeDistrictAPIView, GeoCodeVdcAPIView, InterceptionRecordViewSet, VictimInterviewViewSet
from static_border_stations.views import BorderStationViewSet, StaffViewSet, CommitteeMemberViewSet, LocationViewSet


urlpatterns = patterns('rest_api.views',
    # Budget URLs
    url(r'^budget/$', BudgetViewSet.as_view({'get': 'list', 'post': 'create'}), name='BudgetCalculation'),
    url(r'^budget/(?P<pk>\d+)/$', BudgetViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='BudgetCalculationWithId'),

    # Other items
    url(r'^budget/(?P<parent_pk>\d+)/item/$', OtherItemsViewSet.as_view({'get': 'list_by_budget_sheet', 'post': 'create'}), name='BudgetCalculationWithId'),
    url(r'^budget/(?P<parent_pk>\d+)/item/(?P<pk>\d+)/$', OtherItemsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='BudgetCalculationWithId'),


    # BorderStation URLs
    url(r'^border-station/$', BorderStationViewSet.as_view({'get':'list', 'post':'create'}), name="BorderStations"), # Detail
    url(r'^border-station/(?P<pk>\d+)/$', BorderStationViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="BorderStation"),

    # Staff
    url(r'^staff/$', StaffViewSet.as_view({'get':'list', 'post':'create'}), name="AllStaff"),
    url(r'^staff/(?P<pk>\d+)/$', StaffViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="Staff"),

    # Committee Members
    url(r'^committee-member/$', CommitteeMemberViewSet.as_view({'get':'list', 'post':'create'}), name="CommitteeMembers"),
    url(r'^committee-member/(?P<pk>\d+)/$', CommitteeMemberViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="CommitteeMember"),

    # Locations
    url(r'^location/$', LocationViewSet.as_view({'get':'list', 'post':'create'}), name="Locations"),
    url(r'^location/(?P<pk>\d+)/$', LocationViewSet.as_view({'get':'retrieve', 'put':'update', 'delete':'destroy'}), name="Location"),
    
    # Addresses
    url(r'^address1/$', Address1ViewSet.as_view({'get': 'list', 'post': 'create'}), name='Address1'),
    url(r'^address1/all/$', Address1ViewSet.as_view({'get': 'list_all'}), name='Address1all'),
    url(r'^address1/(?P<pk>\d+)/$', Address1ViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='Address1detail'),

    url(r'^address2/$', Address2ViewSet.as_view({'get': 'list', 'post': 'create'}), name='Address2'),
    url(r'^address2/(?P<pk>\d+)/$', Address2ViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'}), name='Address2detail'),

    # Fuzzy searching for addresses
    url(r'^address1/fuzzy/$', GeoCodeDistrictAPIView.as_view(), name="Address1FuzzySearch"),
    url(r'^address2/fuzzy/$', GeoCodeVdcAPIView.as_view(), name="Address2FuzzySearch"),

    # IRFs
    url(r'^irf/$', InterceptionRecordViewSet.as_view({'get': 'list'}), name="InterceptionRecord"),
    url(r'^irf/(?P<pk>\d+)/$', InterceptionRecordViewSet.as_view({'delete': 'destroy'}), name="InterceptionRecordDetail"),

    # VIFs
    url(r'^vif/$', VictimInterviewViewSet.as_view({'get': 'list'}), name="VictimInterview"),
    url(r'^vif/(?P<pk>\d+)/$', VictimInterviewViewSet.as_view({'delete': 'destroy'}), name="VictimInterviewDetail"),

    #Accounts and DefaultPermissionsSets
    url(r'^login/', views.obtain_auth_token),
    url(r'^me/$', CurrentUserView.as_view(), name="CurrentUser"),

)
