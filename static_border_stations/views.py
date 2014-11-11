from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy

from django.views.generic import CreateView

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet

from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin

from static_border_stations.models import Person,Location
from dataentry.models import BorderStation

from static_border_stations.forms import *
from dataentry.forms import BorderStationForm

class StaffInline(InlineFormSet):
    model=Person
    extra = 1

class CommitteeMemberInline(InlineFormSet):
    model=Person
    extra = 1

class LocationInline(InlineFormSet):
    model=Location
    extra = 1

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