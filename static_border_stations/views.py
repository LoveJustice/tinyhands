from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse_lazy


from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin
from dataentry.models import BorderStation
from dataentry.forms import BorderStationForm
from dataentry.serializers import BorderStationSerializer

from static_border_stations.models import Staff, CommitteeMember, Location
from static_border_stations.serializers import StaffSerializer, CommitteeMemberSerializer, LocationSerializer
from static_border_stations.forms import StaffForm, CommitteeMemberForm

from rest_api.authentication import HasPermission, HasDeletePermission, HasGetPermission, HasPostPermission, HasPutPermission


class FormSetForStations(InlineFormSet):

    def __init__(self, *args, **kwargs):
        super(FormSetForStations, self).__init__(*args, **kwargs)
        if self.request.path.find('create') == -1 and self.request.path.find('update') == -1:
            self.extra = 0
        else:
            self.extra = 1
        return


class BorderStationViewSet(viewsets.ModelViewSet):
    queryset = BorderStation.objects.all()
    serializer_class = BorderStationSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasPostPermission, HasPutPermission)
    permissions_required = ['permission_border_stations_view']
    post_permissions_required = ['permission_border_stations_add']
    put_permissions_required = ['permission_border_stations_edit']
    
    @list_route()
    def list_all(self, request):
      border_stations = BorderStation.objects.all()
      serializer = self.get_serializer(border_stations, many=True)
      return Response(serializer.data)
        

class BorderStationRestAPI(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('border_station',)
    permission_classes = (IsAuthenticated, HasPermission, HasPostPermission, HasPutPermission)
    permissions_required = ['permission_border_stations_view']
    post_permissions_required = ['permission_border_stations_edit']
    put_permissions_required = ['permission_border_stations_edit']


class LocationViewSet(BorderStationRestAPI):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class CommitteeMemberViewSet(BorderStationRestAPI):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer


class StaffViewSet(BorderStationRestAPI):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


    def staff_retrieve(self, request, *args, **kwargs):
        """
            retrieve all the staff for a particular border_station
        """
        self.object_list = self.filter_queryset(self.get_queryset().filter(border_station=self.kwargs['pk']))
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(serializer.data)


class StaffInline(FormSetForStations):
    model = Staff
    form_class = StaffForm


class CommitteeMemberInline(FormSetForStations):
    model = CommitteeMember
    form_class = CommitteeMemberForm

class LocationInline(FormSetForStations):
    model = Location


class StaticBorderStationsCreateView (
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = BorderStation
    template_name = 'static_border_stations/static_border_stations_base.html'
    form_class = BorderStationForm
    success_url = reverse_lazy('home')
    inlines = [StaffInline, CommitteeMemberInline, LocationInline]
    permissions_required = ['permission_border_stations_add']

    def get_context_data(self, **kwargs):
        context = super(StaticBorderStationsCreateView, self).get_context_data(**kwargs)
        context["saved"] = False
        context["is_create"] = True
        return context


class StaticBorderStationsUpdateView (
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = BorderStation
    template_name = 'static_border_stations/static_border_stations_base.html'
    form_class = BorderStationForm
    success_url = reverse_lazy('home')
    inlines = [StaffInline, CommitteeMemberInline, LocationInline]
    permissions_required = ['permission_border_stations_edit']

    def get_context_data(self, **kwargs):
        context = super(StaticBorderStationsUpdateView, self).get_context_data(**kwargs)
        context["saved"] = True
        context["border_station_pk"] = kwargs['form'].instance.id
        return context


class StaticBorderStationsDetailView(StaticBorderStationsUpdateView):
    permissions_required = ['permission_border_stations_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(StaticBorderStationsDetailView, self).get_context_data(**kwargs)
        context["saved"] = True
        context["readonly"] = True
        return context
