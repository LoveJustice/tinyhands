from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, View, CreateView, UpdateView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from django.contrib.auth.decorators import login_required
from dataentry.models import (
    VictimInterview,
    InterceptionRecord,
    Interceptee,
    VictimInterviewPersonBox,
    VictimInterviewLocationBox
)
from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin
from dataentry.forms import (
    InterceptionRecordForm,
    VictimInterviewForm,
    VictimInterviewPersonBoxForm,
    VictimInterviewLocationBoxForm,
)
from datetime import date
from dataentry import export
from django.http import HttpResponse
import csv
import re


@login_required
def home(request):
    return render(request, 'home.html', locals())


class InterceptionRecordListView(
        LoginRequiredMixin,
        ListView):
    model = InterceptionRecord
    paginate_by = 20
    
    def get_queryset(self):
        try:
            value = self.request.GET['search_value']
        except:
            value = ''
        if (value != ''):
            if(value.isnumeric()):
                print "Number"
                object_list = self.model.objects.filter(irf_number__icontains = value)
            else:
                print "String"
                #work more on finding the correct model attributes
                object_list = self.model.objects.filter(staff_name__icontains = value)
            
	else:
	    print "you lose charlie"
            object_list = self.model.objects.all()
        return object_list

class IntercepteeInline(InlineFormSet):
    model = Interceptee
    extra = 12
    max_num = 12


class InterceptionRecordCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_add']

    def forms_valid(self, form, inlines):
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        return super(InterceptionRecordCreateView, self).forms_valid(form, inlines)


class InterceptionRecordUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_edit']


class InterceptionRecordDetailView(InterceptionRecordUpdateView):
    permissions_required = ['permission_irf_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class PersonBoxInline(InlineFormSet):
    model = VictimInterviewPersonBox
    extra = 12

    def get_factory_kwargs(self):
        kwargs = super(PersonBoxInline, self).get_factory_kwargs()
        kwargs['form'] = VictimInterviewPersonBoxForm
        return kwargs


class LocationBoxInline(InlineFormSet):
    model = VictimInterviewLocationBox
    extra = 8

    def get_factory_kwargs(self):
        kwargs = super(LocationBoxInline, self).get_factory_kwargs()
        kwargs['form'] = VictimInterviewLocationBoxForm
        return kwargs


class VictimInterviewListView(
        LoginRequiredMixin,
        ListView):
    model = VictimInterview
    paginate_by = 20

    def get_queryset(self):
        try:
            value = self.request.GET['search_value']
        except:
            value = ''
        if (value != ''):
            if(value.isnumeric()):
                print "Number"
                object_list = self.model.objects.filter(irf_number__icontains = value)
            else:
                print "String"
                #work more on finding the correct model attributes                                                                                                                                                  
                object_list = self.model.objects.filter(staff_name__icontains = value)

        else:
            print "you lose charlie"
            object_list = self.model.objects.all()
        return object_list

class VictimInterviewCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_add']


class VictimInterviewUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_edit']


class VictimInterviewDetailView(VictimInterviewUpdateView):
    permissions_required = ['permission_vif_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class InterceptionRecordCSVExportView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        View):
    permissions_required = ['permission_irf_view']

    def get(self, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        today = date.today()
        response['Content-Disposition'] = 'attachment; filename=irf-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)

        writer = csv.writer(response)
        irfs = InterceptionRecord.objects.all()
        csv_rows = export.get_irf_export_rows(irfs)
        writer.writerows(csv_rows)

        return response


class VictimInterviewCSVExportView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        View):
    permissions_required = ['permission_vif_view']

    def get(self, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        today = date.today()
        response['Content-Disposition'] = 'attachment; filename=vif-all-data-%d-%d-%d.csv' % (today.year, today.month, today.day)

        writer = csv.writer(response)
        vifs = VictimInterview.objects.select_related('person_boxes').select_related('location_boxes').all()
        csv_rows = export.get_vif_export_rows(vifs)
        writer.writerows(csv_rows)

        return response
