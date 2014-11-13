from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy

from django.views.generic import CreateView

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin

from static_border_stations.models import Staff,CommitteeMember,Location
from dataentry.models import BorderStation

from static_border_stations.forms import *
from dataentry.forms import BorderStationForm
import ipdb

class FormSetForStations(InlineFormSet):

    def __init__(self, *args, **kwargs):
        super(FormSetForStations, self).__init__(*args, **kwargs)
        if(self.request.path.find('create') == -1 and self.request.path.find('update') == -1):
            self.extra = 0
        else:
            self.extra = 1
        return 

class StaffInline(FormSetForStations):
    model=Staff

class CommitteeMemberInline(FormSetForStations):
    model=CommitteeMember

class LocationInline(FormSetForStations):
    model=Location

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
    
class StaticBorderStationsDetailView(StaticBorderStationsUpdateView):
    permissions_required = ['permission_border_stations_view']
    
    def post(self, request, *args, **kwargs):
        raise PermissionDenied
