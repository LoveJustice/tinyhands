
from datetime import date
import csv
import json
import os
import re
import shutil
import logging

from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView, View, CreateView, TemplateView

from rest_framework import status
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSet
from braces.views import LoginRequiredMixin
from fuzzywuzzy import process

from dataentry.models import BorderStation, SiteSettings, Address2, Address1, Interceptee, Person, InterceptionRecord, VictimInterview, VictimInterviewLocationBox, VictimInterviewPersonBox
from dataentry.models.alias_group import AliasGroup
from dataentry.forms import IntercepteeForm, InterceptionRecordForm, Address2Form, Address1Form, VictimInterviewForm, VictimInterviewLocationBoxForm, VictimInterviewPersonBoxForm
from dataentry.dataentry_signals import irf_done

from dataentry.serializers import Address1Serializer, Address2Serializer, InterceptionRecordListSerializer, VictimInterviewListSerializer, VictimInterviewSerializer, PersonSerializer, IntercepteeSerializer, InterceptionRecordSerializer, IDManagementSerializer, PersonFormsSerializer
from dataentry.dataentry_signals import irf_done, vif_done
from dataentry.fuzzy_matching import match_location

from export_import import irf_io, vif_io

from accounts.mixins import PermissionsRequiredMixin

from rest_api.authentication import HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission

from dataentry import fuzzy_matching


logger = logging.getLogger(__name__)

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
            if len(stations) != 0:
                object_list = self.model.objects.filter(**{self.Number: value})
                if len(object_list) == 0:
                    object_list = self.model.objects.filter(**{self.Name: value})
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
                filename = "unassociated_photos/irf-photo-%s-index-%s.%s" % (irf_num, interceptee_index, extension)
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


class InterceptionRecordCreateView(LoginRequiredMixin, PermissionsRequiredMixin, IRFImageAssociationMixin,
                                   CreateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = settings.CLIENT_DOMAIN + "/irf"

    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_add']

    def get_context_data(self, **kwargs):
        context = super(InterceptionRecordCreateView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context

    def forms_valid(self, form, inlines):
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        form = form.save()
        interceptees = []
        for formset in inlines:
            interceptee = formset.save()
            interceptees.append(interceptee)
        logger.debug("IRF Create: After save for " + form.irf_number)
        irf_done.send_robust(sender=self.__class__, irf_number=form.irf_number, irf=form, interceptees=interceptees)
        return HttpResponseRedirect(self.get_success_url())


class InterceptionRecordUpdateView(LoginRequiredMixin, PermissionsRequiredMixin, IRFImageAssociationMixin,
                                   UpdateWithInlinesView):
    model = InterceptionRecord
    form_class = InterceptionRecordForm
    success_url = settings.CLIENT_DOMAIN + "/irf"
    inlines = [IntercepteeInline]
    permissions_required = ['permission_irf_edit']

    def get_context_data(self, **kwargs):
        context = super(InterceptionRecordUpdateView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context


    def forms_valid(self, form, inlines):
        form = form.save()
        interceptees = []
        for formset in inlines:
            interceptee = formset.save()
            interceptees.append(interceptee)
        logger.debug("IRF Update: After save for " + form.irf_number)
        irf_done.send_robust(sender=self.__class__, irf_number=form.irf_number, irf=form, interceptees=interceptees)
        return HttpResponseRedirect(self.get_success_url())


class InterceptionRecordDetailView(InterceptionRecordUpdateView):
    permissions_required = ['permission_irf_view']

    def get_context_data(self, **kwargs):
        context = super(InterceptionRecordDetailView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context


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


class VictimInterviewListView(LoginRequiredMixin, SearchFormsMixin, ListView):
    model = VictimInterview

    def __init__(self, *args, **kwargs):
        # Passes what to search by to SearchFormsMixin
        super(VictimInterviewListView, self).__init__(vif_number__icontains="number", interviewer__icontains="name")


class VictimInterviewCreateView(LoginRequiredMixin, PermissionsRequiredMixin, CreateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = settings.CLIENT_DOMAIN + '/vif'
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_add']

    def get_context_data(self, **kwargs):
        context = super(VictimInterviewCreateView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context


    def forms_valid(self, form, inlines):
        form.instance.form_entered_by = self.request.user
        form.instance.date_form_received = date.today()
        form = form.save()
        for formset in inlines:
            formset.save()
        logger.debug("VIF Create: After save for " + form.vif_number)
        vif_done.send_robust(sender=self.__class__,vif_number=form.vif_number, vif=form)
        return HttpResponseRedirect(self.get_success_url())


class VictimInterviewUpdateView(LoginRequiredMixin, PermissionsRequiredMixin, UpdateWithInlinesView):
    model = VictimInterview
    form_class = VictimInterviewForm
    success_url = settings.CLIENT_DOMAIN + '/vif'
    inlines = [PersonBoxInline, LocationBoxInline]
    permissions_required = ['permission_vif_edit']

    def get_context_data(self, **kwargs):
        context = super(VictimInterviewUpdateView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context


    def forms_valid(self, form, inlines):
        form = form.save()
        for formset in inlines:
            formset.save()
        logger.debug("VIF Update: After save for " + form.vif_number)
        vif_done.send_robust(sender=self.__class__,vif_number=form.vif_number, vif=form)
        return HttpResponseRedirect(self.get_success_url())


class VictimInterviewDetailView(VictimInterviewUpdateView):
    permissions_required = ['permission_vif_view']

    def get_context_data(self, **kwargs):
        context = super(VictimInterviewDetailView, self).get_context_data(**kwargs)
        context.update({"CLIENT_DOMAIN": settings.CLIENT_DOMAIN})
        return context

    def post(self, request, *args, **kwargs):
        raise PermissionDenied


class GeoCodeAddress1APIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        value = request.query_params["address1"]
        matches = match_location(address1_name=value)
        if matches:
            serializer = Address1Serializer(matches, many=True)
            return Response(serializer.data)
        else:
            return Response({"id": "-1", "name": "None"})


class GeoCodeAddress2APIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            address1_name = request.query_params["address1"]

        except:
            address1_name = None
        address2_name = request.query_params["address2"]
        matches = match_location(address1_name, address2_name)
        if matches:
            serializer = Address2Serializer(matches, many=True)
            return Response(serializer.data)
        else:
            return Response({"id": "-1", "name": "None"})


class Address2CreateView(LoginRequiredMixin, PermissionsRequiredMixin, CreateView):
    model = Address2
    form_class = Address2Form
    template_name = "dataentry/address2_create_page.html"
    permissions_required = ['permission_vif_add', 'permission_irf_add']

    def form_valid(self, form):
        form.save()
        return HttpResponse(render_to_string('dataentry/address2_create_success.html'))


class Address1CreateView(LoginRequiredMixin, PermissionsRequiredMixin, CreateView):
    model = Address1
    form_class = Address1Form
    template_name = "dataentry/address1_create_page.html"
    permissions_required = ['permission_vif_add', 'permission_irf_add']

    def form_valid(self, form):
        form.save()
        return HttpResponse(render_to_string('dataentry/address1_create_success.html'))


class StationCodeAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        codes = BorderStation.objects.all().values_list("station_code", flat=True)
        return Response(codes, status=status.HTTP_200_OK)


@login_required
def interceptee_fuzzy_matching(request):
    input_name = request.GET['name']
    all_people = Interceptee.objects.all()
    people_dict = {serializers.serialize("json", [obj]): obj.person.full_name for obj in all_people }
    site_settings = SiteSettings.objects.all()[0]
    matches = process.extractBests(input_name, people_dict, score_cutoff=site_settings.get_setting_value_by_name('person_cutoff'), limit=site_settings.get_setting_value_by_name('person_limit'))

    return HttpResponse(json.dumps(matches), content_type="application/json")


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_address2_manage']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('full_name',)
    ordering_fields = ('full_name', 'age', 'gender', 'phone_contact')
    ordering = ('full_name',)

class IDManagementViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = IDManagementSerializer
    permission_classes = (IsAuthenticated, HasPermission)
    permissions_required = ['permission_address2_manage']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('full_name',)
    ordering_fields = ('full_name', 'age', 'gender', 'phone_contact','aliases',
            'form_type','form_number','form_date')
    ordering = ('full_name',)

    def fuzzy_match(self, request):
        input_name = request.GET['name']
        results = fuzzy_matching.match_person(input_name)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    def partial_phone(self, request):
        input_phone = request.GET['phone']
        results = Person.objects.filter(phone_contact__contains=input_phone)
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
    
    def person_forms(self, request):
        person_id = request.GET['person_id']
        person = Person.objects.get(id=person_id)
        forms = person.get_form_data()
        serializer = PersonFormsSerializer(forms, many=True, context={'request': request})
        return Response(serializer.data)
    
    def alias_group(self, request):
        group_id = request.GET['group_id']
        results = Person.objects.filter(alias_group=group_id);
        serializer = IDManagementSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)
    
    def get_person(self, request):
        person_id = request.GET['person_id']
        person = Person.objects.get(id=person_id)
        serializer = IDManagementSerializer(person, context={'request': request})
        return Response(serializer.data)
    
    def add_alias_group(self, request, pk, pk2):
        try:
            person1 = Person.objects.get(id=pk)
            person2 = Person.objects.get(id=pk2)
            alias_group = None
            if person1.alias_group is not None:
                alias_group = person1.alias_group
    
            if person2.alias_group is not None:
                if alias_group is not None:
                    logger.error("Cannot make alias group from two persons where both are already in alias groups")
                    return Response({'detail': "Both persons already in alias group"}, status=status.HTTP_409_CONFLICT)
                alias_group = person2.alias_group
            
            with transaction.atomic():
                if alias_group is None:
                    alias_group = AliasGroup()
                    alias_group.save()
        
                person1.alias_group = alias_group
                person1.save()
                person2.alias_group = alias_group
                person2.save()
        except:
            logger.error('Failed to add to alias group: ' + pk + ' ' + pk2)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({"message": "success!"})
            
    def remove_alias_group (self, request, pk):
        try:
            person = Person.objects.get(id=pk)
            if person.alias_group is None:
                return
            
            with transaction.atomic():
                alias_group = person.alias_group
                person.alias_group = None
                person.save()
                
                # check remaining members of the group
                members = Person.objects.filter(alias_group = alias_group)
                if len(members) < 2:
                    # only one member left in the alias group - delete the alias group
                    for member in members:
                        member.alias_group = None
                        member.save()
                    alias_group.delete()
        except:
            logger.error('Failed to remove from alias group: ' + pk)
            return Response({'detail': "an error occurred"}, status=status.HTTP_404_NOT_FOUND)
                
        return Response({"message": "success!"})
        
           

class InterceptionRecordViewSet(viewsets.ModelViewSet):
    queryset = InterceptionRecord.objects.all()
    serializer_class = InterceptionRecordSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasDeletePermission,)
    permissions_required = ['permission_irf_view']
    delete_permissions_required = ['permission_irf_delete']

    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('irf_number',)
    ordering_fields = (
        'irf_number', 'staff_name', 'number_of_victims', 'number_of_traffickers', 'date_time_of_interception',
        'date_time_entered_into_system', 'date_time_last_updated',)
    ordering = ('date_time_of_interception',)

    def destroy(self, request, *args, **kwargs):
        irf_id = kwargs['pk']
        irf = InterceptionRecord.objects.get(id=irf_id)
        rv = super(viewsets.ModelViewSet, self).destroy(request, args, kwargs)
        logger.debug("After IRF destroy " + irf.irf_number)
        irf_done.send_robust(sender=self.__class__, irf_number=irf.irf_number, irf=None, interceptees=None)
        return rv

    def list(self, request, *args, **kwargs):
        temp = self.serializer_class
        self.serializer_class = InterceptionRecordListSerializer  # we want to use a custom serializer just for the list view
        super_list_response = super(InterceptionRecordViewSet, self).list(request, *args, **kwargs)  # call the supers list view with custom serializer
        self.serializer_class = temp  # put the original serializer back in place
        return super_list_response

    def retrieve(self, request, *args, **kwargs):
        response = {}
        response = super(InterceptionRecordViewSet, self).retrieve(request, *args, **kwargs)
        for field in InterceptionRecord._meta.fields:
            try:
                if field.weight != None:
                    response.data[field.name] = {
                        'value': response.data[field.name],
                        'weight': field.weight
                    }
            except:
                pass
        return response


class IntercepteeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, HasPermission, HasDeletePermission, HasPostPermission, HasPutPermission)
    permissions_required = ['permission_irf_view']
    delete_permissions_required = ['permission_irf_delete']
    post_permissions_required = ['permission_irf_add']
    put_permissions_required = ['permission_irf_edit']

    queryset = Interceptee.objects.all()
    serializer_class = IntercepteeSerializer
    filter_fields = ('interception_record',)


class VictimInterviewViewSet(viewsets.ModelViewSet):
    queryset = VictimInterview.objects.all()
    serializer_class = VictimInterviewListSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasDeletePermission,)
    permissions_required = ['permission_vif_view']
    delete_permissions_required = ['permission_vif_delete']
    filter_backends = (filters.SearchFilter, filters.OrderingFilter,)
    search_fields = ('vif_number',)
    ordering_fields = (
        'vif_number', 'interviewer', 'number_of_victims', 'number_of_traffickers', 'date',
        'date_time_entered_into_system', 'date',
        'date_time_last_updated',)
    ordering = ('date',)


class VictimInterviewDetailViewSet(viewsets.ModelViewSet):
    queryset = VictimInterview.objects.all()
    serializer_class = VictimInterviewSerializer
    permission_classes = (IsAuthenticated, HasPermission, HasDeletePermission,)
    permissions_required = ['permission_vif_view']
    delete_permissions_required = ['permission_vif_delete']

    def destroy(self, request, *args, **kwargs):
        vif_id = kwargs['pk']
        vif = VictimInterview.objects.get(id=vif_id)
        rv = super(viewsets.ModelViewSet, self).destroy(request, args, kwargs)
        logger.debug("After VIF destroy " + vif.vif_number)
        vif_done.send_robust(sender=self.__class__, vif_number=vif.vif_number, vif=None)
        return rv


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def vifExists(request, vif_number):
    try:
        existingVif = VictimInterview.objects.get(vif_number=vif_number)
        return Response(existingVif.vif_number)
    except:
        return Response("Vif does not exist")


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def irfExists(request, irf_number):
    try:
        existingIrf = InterceptionRecord.objects.get(irf_number=irf_number)
        return Response(existingIrf.irf_number)
    except:
        return Response("Irf does not exist")
