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
    VictimInterviewLocationBox,
    District,
    VDC
)
from accounts.mixins import PermissionsRequiredMixin
from braces.views import LoginRequiredMixin
from dataentry.forms import (
    InterceptionRecordForm,
    IntercepteeForm,
    VictimInterviewForm,
    VictimInterviewPersonBoxForm,
    VictimInterviewLocationBoxForm,
    VDCForm,
)
from datetime import date
from dataentry import export
from django.http import HttpResponse
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from dataentry.serializers import DistrictSerializer, VDCSerializer

import csv
import re
from alert_checkers import IRFAlertChecker, VIFAlertChecker
from fuzzy_matching import match_location

@login_required
def home(request):
    return render(request, 'home.html', locals())


class SearchFormsMixin(object):

    Name = None
    Number = None

    def __init__(self, *args, **kw):
        for key, value in kw.iteritems():
            if(value == "name"):
                self.Name = key
            elif(value == "number"):
                self.Number = key

    def get_queryset(self):
        try:
            value = self.request.GET['search_value']
        except:
            value = ''
        if (value != ''):
            if(re.match('\w+\d+$', value) and self.model != VDC):
                object_list = self.model.objects.filter(**{self.Number :value})
            else:
                object_list = self.model.objects.filter(**{self.Name :value})
        else:
            object_list = self.model.objects.all()
        return object_list


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SearchFormsMixin, self).get_context_data(**kwargs)
        # Check if database is empty to change message in search page
        context['database_empty'] = self.model.objects.count()==0
        return context
    
class InterceptionRecordListView(
        LoginRequiredMixin,
	SearchFormsMixin,
        ListView):
    model = InterceptionRecord
    paginate_by = 20

    def __init__(self, *args, **kw):
        #passes what to search by to SearchFormsMixin
        super(InterceptionRecordListView, self).__init__(irf_number__icontains = "number", staff_name__icontains = "name")

class IntercepteeInline(InlineFormSet):
    model = Interceptee
    extra = 12
    max_num = 12

    def get_factory_kwargs(self):
        kwargs = super(IntercepteeInline, self).get_factory_kwargs()
        kwargs['form'] = IntercepteeForm
        return kwargs

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

        IRFAlertChecker(form,inlines).check_them()
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

    def forms_valid(self, form, inlines):
        IRFAlertChecker(form,inlines).check_them()
        return super(InterceptionRecordUpdateView, self).forms_valid(form, inlines)



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
        SearchFormsMixin,
        ListView):
    model = VictimInterview
    paginate_by = 20
    
    def __init__(self, *args, **kwargs):
        #passes what to search by to SearchFormsMixin
        super(VictimInterviewListView, self).__init__(vif_number__icontains = "number", interviewer__icontains = "name")

class VictimInterviewCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_add']

    def forms_valid(self, form, inlines):
        VIFAlertChecker(form,inlines).check_them()
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        return super(VictimInterviewCreateView, self).forms_valid(form, inlines)



class VictimInterviewUpdateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_edit']

    def forms_valid(self, form, inlines):
        VIFAlertChecker(form,inlines).check_them()
        return super(VictimInterviewUpdateView, self).forms_valid(form, inlines)


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


class GeoCodeDistrictAPIView(
        APIView):
    
    def get(self,request):
        value = request.QUERY_PARAMS['district']
        matches = match_location(district_name=value)
        if(matches):
            serializer = DistrictSerializer(matches)
            return Response(serializer.data)
        else:
            return Response({"id": "-1","name":"None"})


class GeoCodeVdcAPIView(APIView):
    
    def get(self, request):
        value = request.QUERY_PARAMS['vdc']
        matches = match_location(vdc_name=value)
        if(matches):
            serializer = VDCSerializer(matches)
            return Response(serializer.data)
        else:
            return Response({"id": "-1","name":"None"})


class VDCAdminView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        SearchFormsMixin,
        ListView):
    model = VDC
    template_name = "dataentry/vdc_admin_page.html"
    permissions_required = ['permission_vdc_manage']
    paginate_by = 20

    def __init__(self, *args, **kwargs):
        super(VDCAdminView, self).__init__(name__icontains = "name")

    def get_context_data(self, **kwargs):
        context = super(VDCAdminView, self).get_context_data(**kwargs)
        context['lower_limit'] = context['page_obj'].number - 5
        context['upper_limit'] = context['page_obj'].number + 5
        context['database_empty'] = self.model.objects.count()==0
        return context

class VDCAdminUpdate(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        UpdateView):
    model = VDC
    form_class = VDCForm
    template_name = "dataentry/vdc_admin_update.html"
    permissions_required = ['permission_vdc_manage']
    
    def dispatch(self, request, *args, **kwargs):
        self.vdc_id = kwargs['pk']
        return super(VDCAdminUpdate, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.save()
        vdc = VDC.objects.get(id=self.vdc_id)
        return HttpResponse(render_to_string('dataentry/vdc_admin_update_success.html'))


class VDCCreateView(
        LoginRequiredMixin,
        PermissionsRequiredMixin,
        CreateView):
    model = VDC
    form_class = VDCForm
    template_name = "dataentry/vdc_create_page.html"
    permissions_required = ['permission_vif_add','permission_irf_add']
    
    def form_valid(self, form):
        form.save()
        return HttpResponse(render_to_string('dataentry/vdc_create_success.html'))