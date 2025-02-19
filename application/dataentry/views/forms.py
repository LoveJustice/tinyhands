import json
import pytz
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import filters as fs
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse

from dataentry.models import BaseForm, BorderStation, Country, FormCategory, Form, FormType, Incident, QuestionLayout, UserLocationPermission
from dataentry.serializers import FormSerializer, FormTypeSerializer, CountrySerializer
from export_import.export_form_csv import IrfCsv, PvfCsv

class RelatedForm:
    def __init__(self, id, form_number, form_type, form_name, staff_name, station_id, country_id, time_entered, time_last_edited):
        self.id = id
        self.form_number = form_number
        self.form_type = form_type
        self.form_name = form_name
        self.staff_name = staff_name
        self.country_id = country_id
        self.station_id = station_id
        self.time_entered = time_entered
        self.time_last_edited = time_last_edited

class RelatedFormsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    form_number = serializers.CharField()
    form_type = serializers.CharField()
    form_name = serializers.CharField()
    staff_name = serializers.CharField()
    country_id = serializers.IntegerField()
    station_id = serializers.IntegerField()
    time_entered = serializers.CharField()
    time_last_edited = serializers.CharField()        

class FormTypeViewSet(viewsets.ModelViewSet):
    queryset = FormType.objects.all()
    serializer_class = FormTypeSerializer
    filter_backends = (fs.SearchFilter, fs.OrderingFilter,)
    ordering_fields = ('name',)
    ordering = ('name',)
    
class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    ordering = ('form_type__name','form_name',)
    
    def list(self, request):
        form_qs = self.queryset
        if 'type_name' in request.GET:
            form_qs = form_qs.filter(form_type__name=request.GET['type_name'])
        if 'station_id' in request.GET:
            form_qs = form_qs.filter(stations__id = request.GET['station_id'])
        serializer = self.get_serializer(form_qs.order_by('form_type__name','form_name'), many=True)
        return Response(serializer.data)
    
    def identifier(self, question):
        self.tag_map[question.form_tag] = question.id
        if hasattr(self, 'identifier_type') and self.identifier_type == 'tag':
            return question.form_tag
        else:
            return question.id
    
    def address_config(self, config, layout):
        config['Address'].append(self.identifier(layout.question))
    
    def date_config(self, config, layout):
        config['Date'].append(self.identifier(layout.question))
    
    def person_config(self, config, layout):
        config['Person'].append(self.identifier(layout.question))
        if layout.form_config is not None and 'RadioItems' in layout.form_config:
            config['RadioOther'].append(self.identifier(layout.question))
            
    def radio_config(self, config, layout):
        if layout.question.params is not None and 'textbox' in layout.question.params:
            config['RadioOther'].append(self.identifier(layout.question))
        else:
            config['Basic'].append(self.identifier(layout.question))
    
    def config_answers(self, config, layouts):
        answer_config = {
            'Address':FormViewSet.address_config,
            'Date': FormViewSet.date_config,
            'Person': FormViewSet.person_config,
            'RadioButton':FormViewSet.radio_config,
            }
        for layout in layouts:
            if layout.question.answer_type.name in answer_config:
                answer_config[layout.question.answer_type.name](self, config, layout)
            else:
                config['Basic'].append(self.identifier(layout.question))
            
            if layout.form_config is not None:
                for key, value in layout.form_config.items():
                    if key == 'RadioItems':
                        for quest, val in value.items():
                            if hasattr(self, 'identifier_type') and self.identifier_type == 'tag':
                                config['RadioItems'][layout.question.form_tag] = val
                            else: 
                                config['RadioItems'][quest] = val
                    elif key == 'FormDefault':
                        config['FormDefault'][self.identifier(layout.question)] = value
                    else:
                        if key == 'question_identifier':
                            key1 = self.identifier(layout.question)
                        else:
                            key1 = key
                        if value == 'question_identifier':
                            value1 = self.identifier(layout.question)
                        else:
                            value1 = value
                        config[key1] = value1

    def form_config(self, request, form_name):
        config = {
            'Person': [],
            'Address':[],
            'Basic':[],
            'Date':[],
            'RadioOther':[],
            'RadioItems':{},
            'FormDefault':{},
            'ExportNames':{},
            'Categories':[],
            'tagMap':{}
            }
        
        self.tag_map = {}
        self.identifier_type = self.request.GET.get('identifier')
        config['useTags'] = self.identifier_type == 'tag'
        form = Form.objects.get(form_name=form_name)
        categories = []
        form_categories = FormCategory.objects.filter(form=form).order_by("order")
        for form_category in form_categories:
            categories.append(form_category.category)
            config['Categories'].append(form_category.name)
        layouts = QuestionLayout.objects.filter(category__in=categories, category__category_type__name='grid').order_by('question__id')
        self.config_answers(config, layouts)
        
        for layout in layouts:
            config['ExportNames'][self.identifier(layout.question)] = layout.question.export_name
        
        form_categories = FormCategory.objects.filter(category__in=categories, category__category_type__name = 'card')
        for formCategory in form_categories:
            config[formCategory.name] = {
                'Category': formCategory.category.id,
                'Category_tag': formCategory.category.form_tag,
                'Person': [],
                'Address':[],
                'Basic':[],
                'Date':[],
                'RadioOther':[],
                'RadioItems':{},
                'FormDefault':{},
                }
            
            layouts = QuestionLayout.objects.filter(category=formCategory.category).order_by('question__id')
            self.config_answers(config[formCategory.name], layouts)
            
            for layout in layouts:
                config['ExportNames'][self.identifier(layout.question)] = layout.question.export_name
        
        if self.identifier_type == 'tag':    
            config['tagMap'] = self.tag_map
        
        return Response(config, status=status.HTTP_200_OK)

    def form_client_json(self, request, form_name):
        form = Form.objects.get(form_name=form_name)
        return Response(form.client_json, status=status.HTTP_200_OK)
    
    def set_forms(self, request, station_id):
        try:
            station = BorderStation.objects.get(id=station_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        current_forms = self.queryset.filter(stations = station)
         
        remove_forms = []    
        for current_form in current_forms:
            found = False
            for new_form in request.data:
                if new_form == current_form.id:
                    found = True
                    break
        
            if not found:
                remove_forms.append(current_form)
        
        add_forms = []        
        for new_form in request.data:
            found = False
            for current_form in current_forms:
                if new_form == current_form.id:
                    found = True
                    break
                
            if not found:
                try:
                    the_form = Form.objects.get(id=new_form)
                    add_forms.append(the_form)
                except ObjectDoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
        
        for the_form in remove_forms:
            the_form.stations.remove(station)
        
        for the_form in add_forms:
            the_form.stations.add(station)
                
        return Response(request.data, status=status.HTTP_200_OK)
    
    def adjust_date_time_for_tz(self, date_time, tz_name):
        tz = pytz.timezone(tz_name)
        date_time.replace(tzinfo=pytz.UTC)
        date_time = date_time.astimezone(tz)
        date_time = date_time.replace(microsecond=0)
        date_time = date_time.replace(tzinfo=None)
        return str(date_time)
    
    def map_form_type(self, form_type, station): 
       mapped = form_type
       if form_type == 'VDF':
           pvf_forms = station.form_set.filter(form_type__name = 'PVF')
           if len(pvf_forms) > 0:
               return 'PVF'
       return mapped
    
    def related_forms(self, request, station_id, form_number):
        station = BorderStation.objects.get(id=station_id)
        if not form_number.startswith(station.station_code):
            return Response({'errors' : ['form number ' + form_number + " does not start with the station code"]},status=status.HTTP_400_BAD_REQUEST)
        
        base_number = form_number
        for idx in range(len(station.station_code), len(form_number)):
            if (form_number[idx] < '0' or form_number[idx] > '9') and form_number[idx] != '_':
                base_number = form_number[:idx]
                break
        
        base_length = len(base_number)
        if base_length <= len(station.station_code):
            return Response({'errors' : ['form number ' + form_number + ' is not in standard format']},status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        incident = Incident.objects.get(incident_number = base_number)
        obj = RelatedForm(incident.id,
                base_number,
                'Incident',
                'Incident',
                getattr(incident, 'staff_name', None),
                incident.station.id,
                incident.station.operating_country.id,
                self.adjust_date_time_for_tz (incident.date_time_entered_into_system, incident.station.time_zone),
                self.adjust_date_time_for_tz (incident.date_time_last_updated, incident.station.time_zone))
        results.append(obj)
        
        forms = Form.objects.filter(stations=station, form_type__name__in=['IRF','CIF','VDF', 'LEGAL_CASE', 'PVF', 'SF','LF'])
        for form in forms:
            form_class = form.storage.get_form_storage_class()
            key_field = form_class.key_field_name()
            form_objects = form_class.objects.filter(Q((key_field+'__startswith', base_number)))
            for form_object in form_objects:
                key_value = form_object.get_key()
                if len(key_value) > base_length and key_value[base_length] >= '0' and key_value[base_length] <= '9':
                    # form number has another digit after the base_number -> not related form
                    continue
                if len(form_object.station.form_set.filter(id=form.id)) < 1:
                    continue
                
                staff_name = getattr(form_object, 'staff_name', None)
                obj = RelatedForm(form_object.id,
                                  form_object.get_key(),
                                  self.map_form_type(form_object.get_form_type_name(), form_object.station),
                                  form.form_name,
                                  staff_name,
                                  form_object.station.id,
                                  form_object.station.operating_country.id,
                                  self.adjust_date_time_for_tz (form_object.date_time_entered_into_system, form_object.station.time_zone),
                                  self.adjust_date_time_for_tz (form_object.date_time_last_updated, form_object.station.time_zone))

                results.append(obj)
        serializer = RelatedFormsSerializer(results, many=True)
            
        return Response(serializer.data)
    
    def get_form_countries(self, request, form_id):
        form = Form.objects.get(id=form_id)
        stations = form.stations.all()
        country_ids = []
        for station in stations:
            country_ids.append(station.operating_country.id)
        countries = Country.objects.filter(id__in=country_ids)
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)
    
    def get_form_versions(self, request, form_id, country_id):
        form = Form.objects.get(id=form_id)
        storage_class = form.find_form_class()
        stations = form.stations.filter(operating_country__id=country_id)
        version_list = storage_class.objects.filter(station__in=stations).values_list('form_version', flat=True)
        version_set = set(version_list)
        if None in version_set:
            version_set.remove(None)
        return Response(sorted(version_set))
        
class FormExportCsv (viewsets.ViewSet):
    def export_csv(self, request):
        form = request.GET.get('form')
        country = request.GET.get('country')
        start = request.GET.get('start')
        end = request.GET.get('end')
        if form is None or start is None or end is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        form_status = request.GET.get('status')
        if form_status is None:
            form_status = 'all'
        tmp = request.GET.get('include_pi')
        if tmp is None or tmp != 'Yes':
            remove_pi = True
        else:
            remove_pi = False
        tmp = request.GET.get('sample')
        if tmp is not None:
            sample = int(tmp)
        else:
            sample = 100
        tmp = request.GET.get('remove_suspects')
        if tmp is not None and tmp == 'No':
            remove_suspects = False
        else:
            remove_suspects = True
        tmp = request.GET.get('red_flags')
        if tmp is not None:
            red_flags = int(tmp)
        else:
            red_flags = 0
        tmp = request.GET.get('case_notes')
        if tmp is None or tmp != 'Yes':
            case_notes = False
        else:
            case_notes = True
        tmp = request.GET.get('evidence_category')
        if tmp is not None and tmp == 'Yes':
            verification_category = True
        else:
            verification_category = False
        tmp = request.GET.get('follow_up')
        if tmp is not None and tmp == 'Yes':
            follow_up = True
        else:
            follow_up = False
        
        if remove_pi:
            action = 'VIEW'
        else:
            action = 'VIEW PI'
        
        if country is None or country == 'all':
            country_list = UserLocationPermission.get_countries_with_permission(request.user.id, form, action)
        else:
            tmp = Country.objects.get(id=country)
            if UserLocationPermission.has_session_permission(request, form, action, tmp.id, None):
                country_list = [tmp]
            else:
                Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if form == 'IRF':
            irf_csv = IrfCsv(country_list, start, end, form_status, remove_pi, sample, remove_suspects, red_flags, case_notes)
            result = irf_csv.perform_export()
        elif form == 'PVF':
            pvf_csv = PvfCsv(country_list, start, end, form_status, remove_pi, sample, verification_category, follow_up)
            result = pvf_csv.perform_export()
        
        
        response = HttpResponse(result['file'].read(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + result['name']
        return response
        
        