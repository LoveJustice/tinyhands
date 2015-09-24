from datetime import date
import csv
import json
import os
import re
import shutil

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.generic import ListView, View, DeleteView, CreateView, UpdateView

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from braces.views import LoginRequiredMixin
from fuzzywuzzy import process

from dataentry.models import (BorderStation, VDC, District,
                              Interceptee, InterceptionRecord,
                              VictimInterview, VictimInterviewLocationBox,
                              VictimInterviewPersonBox)
from dataentry.forms import (IntercepteeForm, InterceptionRecordForm,
                             VDCForm, DistrictForm,
                             VictimInterviewForm,
                             VictimInterviewLocationBoxForm, VictimInterviewPersonBoxForm)
from dataentry import export
from dataentry.serializers import DistrictSerializer, VDCSerializer

from accounts.mixins import PermissionsRequiredMixin

from alert_checkers import IRFAlertChecker, VIFAlertChecker
from fuzzy_matching import match_location, match_staff

@login_required
def home(request):
    return redirect("main_dashboard")


class SearchFormsMixin(object):
    # Will equal name of field to search
    Name = None
    Number = None

    def __init__(self, *args, **kw):
        for key, value in kw.iteritems():
            if value == "name":
                self.Name = key
            elif value == "number":
                self.Number = key

    def get_queryset(self):
        try:
            value = self.request.GET['search_value']
        except:
            value = ''
        if value != '':
            code = value[:3]
            stations = BorderStation.objects.filter(station_code__startswith=code)
            if(len(stations) != 0):
                object_list = self.model.objects.filter(**{self.Number :value})
                if(len(object_list) == 0):
                    object_list = self.model.objects.filter(**{self.Name :value})
            else:
                object_list = self.model.objects.filter(**{self.Name :value})
        else:
            object_list = self.model.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SearchFormsMixin, self).get_context_data(**kwargs)
        # Check if database is empty to change message in search page
        context['database_empty'] = self.model.objects.count() == 0
        return context


class InterceptionRecordListView(LoginRequiredMixin, SearchFormsMixin, ListView):
    model = InterceptionRecord

    def __init__(self, *args, **kw):
        #passes what to search by to SearchFormsMixin
        super(InterceptionRecordListView, self).__init__(irf_number__icontains="number",
                                                         staff_name__icontains="name")


class IntercepteeInline(InlineFormSet):
    model = Interceptee
    extra = 12
    max_num = 12

    def get_factory_kwargs(self):
        kwargs = super(IntercepteeInline, self).get_factory_kwargs()
        kwargs['form'] = IntercepteeForm
        return kwargs


class IRFImageAssociationMixin(object):
    def forms_invalid(self, form, inlines):
        for name, file in self.request.FILES.iteritems():
            match = re.match(r"interceptees-(\d+)-photo", name)
            irf_num = self.request.POST.get("irf_number")

            try:
                extension = file.name.split(".")[-1]
            except Exception:
                extension = None

            if match is not None and irf_num is not None and extension is not None:
                interceptee_index = match.group(1)
                filename = "unassociated_photos/irf-photo-%s-index-%s.%s" % (
                    irf_num,
                    interceptee_index,
                    extension
                )
                default_storage.save(filename, ContentFile(file.read()))

        return super(IRFImageAssociationMixin, self).forms_invalid(form, inlines)

    def forms_valid(self, form, inlines):
        interceptees = inlines[0]
        if not os.path.exists(settings.BASE_DIR + '/media/unassociated_photos/'):
            os.makedirs(settings.BASE_DIR + '/media/unassociated_photos/')
        image_paths = os.listdir(settings.BASE_DIR + '/media/unassociated_photos/')
        for path in image_paths:
            match = re.match(r"irf-photo-(.*)-index-(\d+)\.(.*)", path)
            if match is not None:
                irf_number = match.group(1)
                interceptee_index = int(match.group(2))
                extension = match.group(3)
                full_image_path = settings.BASE_DIR + '/media/unassociated_photos/' + path
                dest_image_path = settings.BASE_DIR + '/media/interceptee_photos/' + path
                if form.instance.irf_number != irf_number:
                    continue
                try:
                    interceptee = interceptees[interceptee_index]
                    shutil.move(full_image_path, dest_image_path)
                    interceptee.instance.photo = dest_image_path
                except IndexError:
                    continue
        return super(IRFImageAssociationMixin, self).forms_valid(form, inlines)


class InterceptionRecordCreateView(LoginRequiredMixin,
                                   PermissionsRequiredMixin,
                                   IRFImageAssociationMixin,
                                   CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_add']

    def forms_valid(self, form, inlines):
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        form = form.save()
        for formset in inlines:
            formset.save()
        IRFAlertChecker(form, inlines).check_them()
        return HttpResponseRedirect(self.get_success_url())


class InterceptionRecordUpdateView(LoginRequiredMixin,
                                   PermissionsRequiredMixin,
                                   IRFImageAssociationMixin,
                                   UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_edit']

    def forms_valid(self, form, inlines):
        form = form.save()
        for formset in inlines:
            formset.save()
        IRFAlertChecker(form, inlines).check_them()
        return HttpResponseRedirect(self.get_success_url())


class InterceptionRecordDetailView(InterceptionRecordUpdateView):
    permissions_required = ['permission_irf_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class InterceptionRecordDeleteView(DeleteView):
    model = InterceptionRecord
    success_url = reverse_lazy('interceptionrecord_list')
    permissions_required = ['permission_irf_edit']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.success_url)


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


class VictimInterviewListView(LoginRequiredMixin,
                              SearchFormsMixin,
                              ListView):
    model = VictimInterview

    def __init__(self, *args, **kwargs):
        # Passes what to search by to SearchFormsMixin
        super(VictimInterviewListView, self).__init__(vif_number__icontains="number",
                                                      interviewer__icontains="name")


class VictimInterviewCreateView(LoginRequiredMixin,
                                PermissionsRequiredMixin,
                                CreateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_add']

    def forms_valid(self, form, inlines):
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        form = form.save()
        for formset in inlines:
            formset.save()
        VIFAlertChecker(form, inlines).check_them()
        return HttpResponseRedirect(self.get_success_url())


class VictimInterviewUpdateView(LoginRequiredMixin,
                                PermissionsRequiredMixin,
                                UpdateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = reverse_lazy('victiminterview_list')
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_edit']

    def forms_valid(self, form, inlines):
        form = form.save()
        for formset in inlines:
            formset.save()
        VIFAlertChecker(form, inlines).check_them()
        return HttpResponseRedirect(self.get_success_url())



class VictimInterviewDetailView(VictimInterviewUpdateView):
    permissions_required = ['permission_vif_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class VictimInterviewDeleteView(DeleteView):
    permissions_required = ['permission_vif_edit']
    model = VictimInterview
    success_url = reverse_lazy('victiminterview_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(self.success_url)


class InterceptionRecordCSVExportView(LoginRequiredMixin,
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


class VictimInterviewCSVExportView(LoginRequiredMixin,
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


class GeoCodeDistrictAPIView(APIView):
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



class VDCAdminView(LoginRequiredMixin,
                   PermissionsRequiredMixin,
                   SearchFormsMixin,
                   ListView):
    model = VDC
    template_name = "dataentry/vdc_admin_page.html"
    permissions_required = ['permission_vdc_manage']

    def __init__(self, *args, **kwargs):
        super(VDCAdminView, self).__init__(name__icontains = "name")

    def get_context_data(self, **kwargs):
        context = super(VDCAdminView, self).get_context_data(**kwargs)
        context['database_empty'] = self.model.objects.count()==0
        return context

class VDCAdminUpdate(LoginRequiredMixin,
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


class VDCCreateView(LoginRequiredMixin,
                    PermissionsRequiredMixin,
                    CreateView):
    model = VDC
    form_class = VDCForm
    template_name = "dataentry/vdc_create_page.html"
    permissions_required = ['permission_vif_add','permission_irf_add']

    def form_valid(self, form):
        form.save()
        return HttpResponse(render_to_string('dataentry/vdc_create_success.html'))

class DistrictAdminView(LoginRequiredMixin,
                        PermissionsRequiredMixin,
                        SearchFormsMixin,
                        ListView):
    model = District
    template_name = "dataentry/district_admin_page.html"
    permissions_required = ['permission_vdc_manage']

    def __init__(self, *args, **kwargs):
        super(DistrictAdminView, self).__init__(name__icontains = "name")

    def get_context_data(self, **kwargs):
        context = super(DistrictAdminView, self).get_context_data(**kwargs)
        context['database_empty'] = self.model.objects.count()==0
        return context

class DistrictAdminUpdate(LoginRequiredMixin,
                          PermissionsRequiredMixin,
                          UpdateView):
    model = District
    form_class = DistrictForm
    template_name = "dataentry/district_admin_update.html"
    permissions_required = ['permission_vdc_manage']

    def dispatch(self, request, *args, **kwargs):
        self.district_id = kwargs['pk']
        return super(DistrictAdminUpdate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        district = District.objects.get(id=self.district_id)
        return HttpResponse(render_to_string('dataentry/district_admin_update_success.html'))

class DistrictCreateView(LoginRequiredMixin,
                         PermissionsRequiredMixin,
                         CreateView):
    model = District
    form_class = DistrictForm
    template_name = "dataentry/district_create_page.html"
    permissions_required = ['permission_vif_add','permission_irf_add']

    def form_valid(self, form):
        form.save()
        return HttpResponse(render_to_string('dataentry/district_create_success.html'))


class StationCodeAPIView(APIView):
    def get(self, request):
        codes = BorderStation.objects.all().values_list("station_code", flat=True)
        return Response(codes, status=status.HTTP_200_OK);







@login_required
def interceptee_fuzzy_matching(request):
    input_name = request.GET['name']
    all_people = Interceptee.objects.all()
    people_dict = {serializers.serialize("json", [obj]):obj.full_name for obj in all_people }
    matches = process.extractBests(input_name, people_dict, limit = 10)
    return HttpResponse(json.dumps(matches), content_type="application/json")

def get_station_id(request):
    code = request.GET['code']
    #code = "DNG"
    if code == '':
        return HttpResponse([-1])
    else:
        station = BorderStation.objects.filter(station_code=code)
        if len(station) > 0:
            print("Station id is: " + str(station))
            return HttpResponse([station[0].id])
        else:
            print("No station id")
            return HttpResponse([-1])

