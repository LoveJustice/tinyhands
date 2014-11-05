from datetime import date
import csv
import re
import os
import shutil

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, View, DeleteView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from django.contrib.auth.decorators import login_required
from braces.views import LoginRequiredMixin
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from dataentry.models import (
    VictimInterview,
    InterceptionRecord,
    Interceptee,
    VictimInterviewPersonBox,
    VictimInterviewLocationBox,
    District
)
from accounts.mixins import PermissionsRequiredMixin
from dataentry.forms import (
    InterceptionRecordForm,
    VictimInterviewForm,
    VictimInterviewPersonBoxForm,
    VictimInterviewLocationBoxForm,
)
from dataentry import export
from dataentry.serializers import DistrictSerializer, IntercepteeSerializer
from alert_checkers import IRFAlertChecker, VIFAlertChecker


@login_required
def home(request):
    return render(request, 'home.html', locals())


class SearchFormsMixin(object):
    Name = None
    Number = None

    def __init__(self, *args, **kw):
        for key, value in kw.iteritems():
            if (value == "name"):
                self.Name = key
            elif (value == "number"):
                self.Number = key

    def get_queryset(self):
        try:
            value = self.request.GET['search_value']
        except:
            value = ''
        if (value != ''):
            if (re.match('\w+\d+$', value)):
                object_list = self.model.objects.filter(**{self.Number: value})
            else:
                object_list = self.model.objects.filter(**{self.Name: value})
        else:
            object_list = self.model.objects.all()
        return object_list


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SearchFormsMixin, self).get_context_data(**kwargs)
        # Check if database is empty to change message in search page
        context['database_empty'] = self.model.objects.count() == 0
        return context


class InterceptionRecordListView(
    LoginRequiredMixin,
    SearchFormsMixin,
    ListView):
    model = InterceptionRecord
    paginate_by = 20

    def __init__(self, *args, **kw):
        # passes what to search by to SearchFormsMixin
        super(InterceptionRecordListView, self).__init__(irf_number__icontains="number", staff_name__icontains="name")


class IntercepteeInline(InlineFormSet):
    model = Interceptee
    extra = 12
    max_num = 12


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


class InterceptionRecordCreateView(
    LoginRequiredMixin,
    PermissionsRequiredMixin,
    IRFImageAssociationMixin,
    CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_add']

    def forms_valid(self, form, inlines):
        import pdb

        pdb.set_trace()

        IRFAlertChecker(form, inlines).check_them()
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        return super(InterceptionRecordCreateView, self).forms_valid(form, inlines)


class InterceptionRecordUpdateView(
    LoginRequiredMixin,
    PermissionsRequiredMixin,
    IRFImageAssociationMixin,
    UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = reverse_lazy('interceptionrecord_list')
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_edit']

    def post(self, request, pk):
        # print(request)
        # raw_input("slkdfjadsklj")
        return super(InterceptionRecordUpdateView, self).post(request)

    def forms_valid(self, form, inlines):
        IRFAlertChecker(form, inlines).check_them()
        return super(InterceptionRecordUpdateView, self).forms_valid(form, inlines)


class InterceptionRecordDetailView(InterceptionRecordUpdateView):
    permissions_required = ['permission_irf_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class InterceptionRecordDeleteView(DeleteView):
    model = InterceptionRecord
    success_url = reverse_lazy('interceptionrecord_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.is_superuser:
            self.object.delete()
        else:
            messages.error(request, "You have no power here!!!")
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


class VictimInterviewListView(
    LoginRequiredMixin,
    SearchFormsMixin,
    ListView):
    model = VictimInterview
    paginate_by = 20

    def __init__(self, *args, **kwargs):
        # passes what to search by to SearchFormsMixin
        super(VictimInterviewListView, self).__init__(vif_number__icontains="number", interviewer__icontains="name")


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
        VIFAlertChecker(form, inlines).check_them()
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
        VIFAlertChecker(form, inlines).check_them()
        return super(VictimInterviewUpdateView, self).forms_valid(form, inlines)


class VictimInterviewDetailView(VictimInterviewUpdateView):
    permissions_required = ['permission_vif_view']

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class VictimInterviewDeleteView(DeleteView):
    model = VictimInterview
    success_url = reverse_lazy('victiminterview_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user.is_superuser:
            self.object.delete()
        else:
            messages.error(request, "You have no power here!!!")
        return HttpResponseRedirect(self.success_url)


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


class GeoCodeDistrictAPIView(APIView):
    def get(self, request, id):
        district = District.objects.get(pk=id)
        serializer = DistrictSerializer(district)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @api_view(['GET'])
    def get_district_with_ajax(request, id):
        district = District.objects.get(name="Achham")
        serializer = DistrictSerializer(district, data=request.DATA)
        if serializer.is_valid():
            serializer.object.name = District.objects.filter(name="Achham")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
def interceptee_fuzzy_matching(request):
    # add additional filters for age and phone #?
    if 'name' not in request.GET\
        and 'phone' not in request.GET\
        and 'age' not in request.GET:
        return JsonResponse({
            'success': False,
            'data': "You must pass at least one parameter"
        })
    name = request.GET['name'] if 'name' in request.GET else None
    phone = request.GET['phone'] if 'phone' in request.GET else None
    age = request.GET['age'] if 'age' in request.GET else None
    matches = Interceptee.objects.fuzzy_match_on(name, age, phone)
    print matches
    print matches[0]
    print matches[0][2]
    print JSONRenderer().render(IntercepteeSerializer([matches[0][2]]).data)

    jsonified_matches = []
    for tup in matches:
        interceptee = tup[2]
        json = JSONRenderer().render(IntercepteeSerializer([interceptee]).data)
        jsonified_matches.append((tup[0], tup[1], json))
    return JsonResponse({
        'success': True,
        'data': jsonified_matches
    })


@login_required
def matching_modal(request, id):
    if not id:
        return HttpResponse("You must pass parameter 'id'<br/>Example: /matching_modal/1")
    person = Interceptee.objects.get(pk=id)
    name = request.GET['name'] if 'name' in request.GET else None
    phone = request.GET['phone'] if 'phone' in request.GET else None
    age = request.GET['age'] if 'age' in request.GET else None
    return render(request, "dataentry/matching_modal.html", {
        "person": person,
        "form_name": name,
        "form_phone": phone,
        "form_age": age
    })
