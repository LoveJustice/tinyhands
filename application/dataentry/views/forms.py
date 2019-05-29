import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from dataentry.models import BorderStation, FormCategory, Form, FormType, QuestionLayout
from dataentry.serializers import FormSerializer, FormTypeSerializer

class FormTypeViewSet(viewsets.ModelViewSet):
    queryset = FormType.objects.all()
    serializer_class = FormTypeSerializer
    ordering = ('name',)
    
class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    ordering = ('form_type__name','name',)
    
    def list(self, request):
        form_qs = self.queryset
        if 'type_name' in request.GET:
            form_qs = form_qs.filter(form_type__name=request.GET['type_name'])
        if 'station_id' in request.GET:
            form_qs = form_qs.filter(stations__id = request.GET['station_id'])
        serializer = self.get_serializer(form_qs, many=True)
        return Response(serializer.data)
    
    @staticmethod
    def address_config(config, layout):
        config['Address'].append(layout.question.id)
    
    @staticmethod
    def date_config(config, layout):
        config['Date'].append(layout.question.id)
    
    @staticmethod
    def person_config(config, layout):
        config['Person'].append(layout.question.id)
        if layout.form_config is not None and 'RadioItems' in layout.form_config:
            config['RadioOther'].append(layout.question.id)
            
    @staticmethod
    def radio_config(config, layout):
        if layout.question.params is not None and 'textbox' in layout.question.params:
            config['RadioOther'].append(layout.question.id)
        else:
            config['Basic'].append(layout.question.id)
    
    def config_answers(self, config, layouts):
        answer_config = {
            'Address':FormViewSet.address_config,
            'Date': FormViewSet.date_config,
            'Person': FormViewSet.person_config,
            'RadioButton':FormViewSet.radio_config,
            }
        for layout in layouts:
            if layout.question.answer_type.name in answer_config:
                answer_config[layout.question.answer_type.name](config, layout)
            else:
                config['Basic'].append(layout.question.id)
            
            if layout.form_config is not None:
                for key, value in layout.form_config.items():
                    if key == 'RadioItems':
                        for quest, val in value.items():
                            config['RadioItems'][quest] = val
                    elif key == 'FormDefault':
                        config['FormDefault'][layout.question.id] = value
                    else:
                        config[key] = value

    def form_config(self, request, form_name):
        config = {
            'Person': [],
            'Address':[],
            'Basic':[],
            'Date':[],
            'RadioOther':[],
            'RadioItems':{},
            'FormDefault':{},
            }
        
        form = Form.objects.get(form_name=form_name)
        categories = []
        form_categories = FormCategory.objects.filter(form=form)
        for form_category in form_categories:
            categories.append(form_category.category)
        layouts = QuestionLayout.objects.filter(category__in=categories, category__category_type__name='grid').order_by('question__id')
        self.config_answers(config, layouts)
        
        form_categories = FormCategory.objects.filter(category__in=categories, category__category_type__name = 'card')
        for formCategory in form_categories:
            config[formCategory.name] = {
                'Category': formCategory.category.id,
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
        
        return Response(config, status=status.HTTP_200_OK)       
    
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
        