import json
import datetime
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
from django.db.models import Q
from django.db import transaction
from dataentry.serialize_form import FormDataSerializer
from dataentry.serializers import CountrySerializer
from dataentry.dataentry_signals import form_done

from dataentry.form_data import Form, FormData
from dataentry.models import AutoNumber, BorderStation, Country, FormLog, FormType, UserLocationPermission

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
    def build_query_filter(self, status_list, station_list, in_progress, account_id):
        if in_progress:
            q_filter = Q(status='in-progress')&Q(form_entered_by__id=account_id)
        else:
            q_filter = Q()
        
        q_filter = q_filter | Q(status__in=status_list)&Q(station__in=station_list)
        
        return q_filter
    
    def get_queryset(self):
        if self.action != 'list':
            return None
        in_country = self.request.GET.get('country_ids')
        status = self.request.GET.get('status', 'approved')
        search = self.request.GET.get('search')
        
        status_list = []
        in_progress=False
        for stat in status.split(','):
            # Earlier feature to only allow author to view in-progress forms
            # has been disabled
            #if stat == 'in-progress':
            #    in_progress = True
            #else:
            #    status_list.append(stat)
            status_list.append(stat)
                
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
        form_storage_list = []
        tmp_station_list = BorderStation.objects.filter(operating_country__in=country_list)
        perm_list = UserLocationPermission.objects.filter(account__id=account_id, permission__permission_group=self.get_perm_group_name()).exclude(permission__action='ADD')
        self.serializer_context = {'perm_list':perm_list}
        for station in tmp_station_list:
            form_list = Form.objects.filter(form_type__name=self.get_form_type_name(), stations=station)
            if len(form_list) > 0 and UserLocationPermission.has_permission_in_list(perm_list, self.get_perm_group_name(), None, station.operating_country.id, station.id):
                station_list.append(station)
                form = Form.current_form(self.get_form_type_name(), station.id)
                if form is not None and form.storage not in form_storage_list:
                    form_storage_list.append(form.storage)
        
        q_filter = self.build_query_filter(status_list, station_list, in_progress, account_id)
        queryset = None
        for form_storage in form_storage_list:
            mod = __import__(form_storage.module_name, fromlist=[form_storage.form_model_name])
            form_model = getattr(mod, form_storage.form_model_name)
            
            tmp_queryset = form_model.objects.filter(q_filter).only(*self.get_list_field_names())      
            if search is not None:
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
            #print(request_string)
            request_json = json.loads(request_string)
            self.request_json = request_json
            
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

    def logbook_submit(self, form_data):
        if not hasattr(form_data.form_object, 'logbook_submitted'):
            return
        
        if form_data.form_object.logbook_submitted is None and form_data.form_object.status != 'in-progress':
            form_data.form_object.logbook_submitted = datetime.datetime.now().date()
            form_data.form_object.save()
    
    def pre_process(self, request, form_data):
        pass
    
    def post_process(self, request, form_data):
        pass
    
    def post_create(self, form_data):
        pass
    
    def check_form_number(self, form_data):
        if hasattr(form_data.form_object, 'station'):
            auto_number = form_data.form_object.station.auto_number
        else:
            return True
        if auto_number is None or auto_number != form_data.form.form_type.name:
            return True
        
        form_number = form_data.form_object.get_key()
        return AutoNumber.check_number(form_data.form_object.station, form_data.form, form_number)
    
    # Override in subclass to enable common master person
    def has_common_master_person(self):
        return False
    
    #Override in subclass when common master person is enabled
    def get_common_master_person(self, form):
        return None
    
    # Override in subclass to provide details
    def get_form_log_detail(self, form_object):
        return None
    
    def form_log(self, request, form, form_object, action, request_json):
        form_number = form_object.get_key()
        if form_number is None:
            form_number = 'No Form Number'
        form_log = FormLog()
        form_log.performed_by = request.user
        form_log.form_name = form.form_name
        form_log.form_number = form_number
        form_log.form_id = form_object.id
        form_log.action = action
        form_log.details = self.get_form_log_detail(form_object)
        form_log.request = request_json
        form_log.save()
    
    def create(self, request):
        form_type = FormType.objects.get(name=self.get_form_type_name())
        request_json = self.extract_data(request, self.get_element_paths())
        self.serializer_context = {'form_type':form_type, 'request.user':request.user, 'creation_date':datetime.datetime.now().date()}
        if self.has_common_master_person():
            self.serializer_context['common_master_person'] = {'value':None}
        self.pre_process(request, None)
        transaction.set_autocommit(False)
        try:
            serializer = FormDataSerializer(data=request_json, context=self.serializer_context)
            if serializer.is_valid():
                if not UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'ADD',
                        serializer.get_country_id(), serializer.get_station_id()):
                    transaction.rollback()
                    transaction.set_autocommit(True)
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                try:
                    form_data = serializer.save()
                    if self.check_form_number(form_data):
                        self.post_create(form_data)
                        self.logbook_submit(form_data)
                        serializer2 = FormDataSerializer(form_data, context=self.serializer_context)
                        form_done.send_robust(sender=self.__class__, form_data=form_data)
                        ret = serializer2.data
                        rtn_status = status.HTTP_200_OK
                        # Trying here because this log is failing for project "forms" where form_number is not included
                        try:
                            self.form_log(request, form_data.form, form_data.form_object, 'create', request_json)
                        except:
                            print('No form number')
                        transaction.commit()
                        transaction.set_autocommit(True)
                        self.post_process(request, form_data)
                    else:
                        transaction.rollback()
                        transaction.set_autocommit(True)
                        ret = {
                            'errors':['Form number exceeds highest number allocated for station'],
                            'warnings':[]
                            }
                        rtn_status=status.HTTP_400_BAD_REQUEST
                except IntegrityError as exc:
                    transaction.rollback()
                    transaction.set_autocommit(True)
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
                transaction.rollback()
                transaction.set_autocommit(True)
                ret = {
                    'errors': serializer.the_errors,
                    'warnings':serializer.the_warnings
                    }
                rtn_status=status.HTTP_400_BAD_REQUEST
        except Exception:
            transaction.rollback()
            transaction.set_autocommit(True)
            ret = {
                    'errors': 'Internal Error:' + traceback.format_exc(),
                    'warnings':[]
                }
            rtn_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return Response (ret, status=rtn_status)
    
    def custom_create_blank(self, form_object):
        pass
    
    def retrieve_blank_form(self, request, station_id):
        self.serializer_context = {}
        form = Form.current_form(self.get_form_type_name(), station_id)
        if form is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        form_class = FormData.get_form_class(form)
        the_form = form_class()
        self.custom_create_blank(the_form)
        if station_id is not None:
            station = BorderStation.objects.get(id=station_id)
            the_form.station = station
            add_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'ADD', 
                    the_form.station.operating_country.id, the_form.station.id)
            if not add_access:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if station.auto_number is not None and station.auto_number == form.form_type.name:
                the_number = AutoNumber.get_next_number(station, form)
                setattr(the_form, form_class.key_field_name(), the_number)
        
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
        
        
        if hasattr(the_form, 'station'):
            station = the_form.station
        else:
            station = BorderStation.objects.get(id=pk)
            
        read_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'VIEW', station.operating_country.id, station.id)
        edit_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'EDIT', station.operating_country.id, station.id)
        private_access = UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'VIEW PI', station.operating_country.id, station.id)
        
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
        self.pre_process(request, form_data)
        request_json = self.extract_data(request, self.get_element_paths())

        if getattr(form_data.form_object, 'date_time_entered_into_system', None) is not None:
            creation_date = form_data.form_object.date_time_entered_into_system.date()
        else:
            creation_date = datetime.datetime.now().date()
        self.serializer_context = {'form_type':form.form_type, 'request.user':request.user, 'creation_date':creation_date}
        if self.has_common_master_person():
            self.serializer_context['common_master_person'] = {'value':self.get_common_master_person(the_form)}
        transaction.set_autocommit(False)
        try:
            serializer = FormDataSerializer(form_data, data=request_json, context=self.serializer_context)
            if serializer.is_valid():
                if not UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'EDIT',
                        serializer.get_country_id(), serializer.get_station_id()):
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                form_data = serializer.save()
                if self.check_form_number(form_data):
                    self.logbook_submit(form_data)
                    serializer2 = FormDataSerializer(form_data, context=self.serializer_context)
                    form_done.send_robust(sender=self.__class__, form_data=form_data)
                    rtn_status = status.HTTP_200_OK
                    ret = serializer2.data
                    # Trying here because this log is failing for project "forms" where form_number is not included
                    try:
                        self.form_log(request, form_data.form, form_data.form_object, 'update', request_json)
                    except:
                        print('No form number')
                    transaction.commit()
                    transaction.set_autocommit(True)
                    self.post_process(request, form_data)

                else:
                    transaction.rollback()
                    transaction.set_autocommit(True)
                    ret = {
                        'errors':['Form number exceeds highest number allocated for station'],
                        'warnings':[]
                        }
                    rtn_status=status.HTTP_400_BAD_REQUEST
            else:
                transaction.rollback()
                transaction.set_autocommit(True)
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
            transaction.rollback()
            transaction.set_autocommit(True)
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
        
        if not UserLocationPermission.has_session_permission(request, self.get_perm_group_name(), 'DELETE',
                the_form.station.operating_country.id, the_form.station.id):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        form_data = FormData(the_form, form)
        # Trying here because this log is failing for project "forms" where form_number is not included
        try:
            self.form_log(request, form, the_form, 'destroy', None)
        except:
            print('No form number')
        form_data.delete()
        
        form_done.send_robust(sender=self.__class__, form_data=form_data, remove=True)
        return Response(status=status.HTTP_200_OK)
    
