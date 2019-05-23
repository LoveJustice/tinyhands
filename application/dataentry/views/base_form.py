import json
import traceback

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import filters as fs
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.db import IntegrityError
from dataentry.serialize_form import FormDataSerializer
from dataentry.serializers import CountrySerializer
from dataentry.dataentry_signals import form_done

from dataentry.form_data import Form, FormData
from dataentry.models import BorderStation, Country, FormType, UserLocationPermission

class BorderStationOverviewSerializer(serializers.ModelSerializer):
    operating_country = CountrySerializer()
    class Meta:
        fields = [
            'id',
            'station_code',
            'station_name',
            'operating_country',
        ]
        model = BorderStation


class BaseFormViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if self.action != 'list':
            return None
        in_country = self.request.GET.get('country_ids')
        status = self.request.GET.get('status', 'approved')
        search = self.request.GET.get('search')
                
        countries = Country.objects.all()
        all_country_list = []
        for country in countries:
            all_country_list.append(country.id)
        
        country_list = []
        if in_country is not None and in_country != '':
            # client provided a list of countries to consider
            for cntry in in_country.split(','):
                country_list.append(int(cntry))
        else:
            # client did not provide a list - so consider all countries
           country_list = all_country_list
        
        account_id = self.request.user.id
        
        station_list = []
        form_list = []
        tmp_station_list = BorderStation.objects.filter(operating_country__in=country_list)
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group=self.get_perm_group_name()).exclude(permission__action='ADD')
        self.serializer_context = {'perm_list':perm_list}
        for station in tmp_station_list:
            if (UserLocationPermission.has_permission_in_list(perm_list, self.get_perm_group_name(), None, station.operating_country.id, station.id)):
                station_list.append(station)
                form = Form.current_form(self.get_form_type_name(), station.id)
                if form is not None and form not in form_list:
                    form_list.append(form)
        
        queryset = None
        for form in form_list:
            mod = __import__(form.storage.module_name, fromlist=[form.storage.form_model_name])
            form_model = getattr(mod, form.storage.form_model_name)
            
            tmp_queryset = form_model.objects.filter(station__in=station_list, status=status).only(*self.get_list_field_names())
            
            # If query is for in-progress status CIFs, only include CIFs that were entered by the requesters account
            if status == 'in-progress':
                tmp_queryset = tmp_queryset.filter(form_entered_by__id=account_id)
                
            if search is not None:
                print ('queryset count1', tmp_queryset.count())
                tmp_queryset = self.filter_key(tmp_queryset, search)
            
            if queryset is None:
                queryset = tmp_queryset
            else:
                queryset = queryset.union(tmp_queryset)
            
        if queryset is None:
            queryset = self.get_empty_queryset()
                
        return queryset
    
    def save_files(self, files, subdirectory):
        for file_obj in files:
            filename = file_obj.name
            with default_storage.open(subdirectory + filename, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
                    
    def extract_data(self, request, element_paths):
        if 'main' in request.data:
            request_string = request.data['main']
            request_json = json.loads(request_string)
            
            for element_path in element_paths:
                cnt = 0
                upload = []
                while element_path['element'] + '[' + str(cnt) + ']' in request.data:
                    upload.append(request.data[element_path['element'] + '[' + str(cnt) + ']'])
                    cnt += 1
                
                if len(upload) > 0:
                    self.save_files(upload, element_path['path'])
        else:
            request_json = None
        
        return request_json
    
    def create(self, request):
        form_type = FormType.objects.get(name=self.get_form_type_name())
        request_json = self.extract_data(request, self.get_element_paths())
        self.serializer_context = {'form_type':form_type, 'request.user':request.user}
        try:
            serializer = FormDataSerializer(data=request_json, context=self.serializer_context)
            if serializer.is_valid():
                if not UserLocationPermission.has_session_permission(request, self.get_form_type_name(), 'ADD',
                        serializer.get_country_id(), serializer.get_station_id()):
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                try:
                    form_data = serializer.save()
                    serializer2 = FormDataSerializer(form_data, context=self.serializer_context)
                    form_done.send_robust(sender=self.__class__, form_data=form_data)
                    ret = serializer2.data
                    rtn_status = status.HTTP_200_OK
                except IntegrityError as exc:
                    if 'unique constraint' in exc.args[0]:
                        ret = {
                            'errors': [ exc.args[0] ],
                            'warnings':[]
                        }
                        rtn_status=status.HTTP_400_BAD_REQUEST
                    else:
                        ret = {
                            'errors': 'Internal Error:' + traceback.format_exc(),
                            'warnings':[]
                        }
                        rtn_status=status.HTTP_400_BAD_REQUEST
            else:
                ret = {
                    'errors': serializer.the_errors,
                    'warnings':serializer.the_warnings
                    }
                rtn_status=status.HTTP_400_BAD_REQUEST
        except Exception:
            ret = {
                    'errors': 'Internal Error:' + traceback.format_exc(),
                    'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        return Response (ret, status=rtn_status)
    
    def retrieve_blank_form(self, request, station_id):
        self.serializer_context = {}
        form = Form.current_form(self.get_form_type_name(), station_id)
        if form is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        form_class = FormData.get_form_class(form)
        the_form = form_class()
        station = BorderStation.objects.get(id=station_id)
        the_form.station = station
        add_access = UserLocationPermission.has_session_permission(request, self.get_form_type_name(), 'ADD', 
                    the_form.station.operating_country.id, the_form.station.id)
        if not add_access:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        form_data = FormData(the_form, form)
        serializer = FormDataSerializer(form_data, context=self.serializer_context)
        return Response(serializer.data)
    
    def my_retrieve(self, request, station_id, pk):
        self.serializer_context = {}
        form = Form.current_form(self.get_form_type_name(), station_id)
        if form is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            the_form = FormData.find_object_by_id(pk, form)
            if the_form is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        read_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'VIEW', the_form.station.operating_country.id, the_form.station.id)
        edit_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'EDIT', the_form.station.operating_country.id, the_form.station.id)
        private_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'VIEW PI', the_form.station.operating_country.id, the_form.station.id)
        
        if not read_access:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
                
        if not edit_access and not private_access:
            self.serializer_context['mask_private'] = True
            
        form_data = FormData(the_form, form)
        serializer = FormDataSerializer(form_data, context=self.serializer_context)
        
        resp_data = serializer.data
       
        return Response(resp_data)
    
    def update(self, request, station_id, pk):
        form = Form.current_form(self.get_form_type_name(), station_id)
        the_form = FormData.find_object_by_id(pk, form)
        if the_form is None:
            return Response({'errors' : [self.get_form_type_name() + " not found"], 'warnings':[]}, status=status.HTTP_404_NOT_FOUND)
        form_data = FormData(the_form, form)
        request_json = self.extract_data(request, self.get_element_paths())

        self.serializer_context = {'form_type':form.form_type}
        try:
            serializer = FormDataSerializer(form_data, data=request_json, context=self.serializer_context)
        
            if serializer.is_valid():
                if not UserLocationPermission.has_session_permission(request, self.get_form_type_name(), 'EDIT',
                        serializer.get_country_id(), serializer.get_station_id()):
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                form_data = serializer.save()
                serializer2 = FormDataSerializer(form_data, context=self.serializer_context)
                form_done.send_robust(sender=self.__class__, form_data=form_data)
                rtn_status = status.HTTP_200_OK
                ret = serializer2.data
            else:
                if serializer.the_errors is not None and len(serializer.the_errors) > 0:
                    rtn_errors = serializer.the_errors
                else:
                    rtn_errors = []
                    
                if serializer.the_warnings is not None and len(serializer.the_warnings) > 0:
                    rtn_warnings = serializer.the_warnings
                else:
                    rtn_warnings = []
                
                if len(rtn_errors) < 1 and len(rtn_warnings) < 1:
                    rtn_errors = serializer._errors
                ret = {
                    'errors': rtn_errors,
                    'warnings':rtn_warnings
                    }
                rtn_status = status.HTTP_400_BAD_REQUEST
        except Exception:
            ret = {
                'errors': 'Internal Error:' + traceback.format_exc(),
                'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
       
        return Response (ret, status=rtn_status)
    
    def destroy(self, request, station_id, pk):
        form = Form.current_form(self.get_form_type_name(), station_id)
        try:
            the_form = FormData.find_object_by_id(pk, form)
        except ObjectDoesNotExist:
            return Response({'errors' : [self.get_form_type_name() + " not found"], 'warnings':[]}, status=status.HTTP_404_NOT_FOUND)
        
        if not UserLocationPermission.has_session_permission(request, self.get_form_type_name(), 'DELETE',
                the_form.station.operating_country.id, the_form.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        form_data = FormData(the_form, form)
        form_data.delete()
        form_done.send_robust(sender=self.__class__, form_data=form_data, remove=True)
        return Response(status=status.HTTP_200_OK)
    