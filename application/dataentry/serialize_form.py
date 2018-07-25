import json
import pytz
from django.conf import settings
from dateutil import parser
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_naive, localtime, make_aware
import traceback

from dataentry.models.addresses import Address1, Address2
from dataentry.models.border_station import BorderStation
from dataentry.models.form import Answer, Category, Form, Question, QuestionLayout
from dataentry.models.person import Person
from .form_data import FormData, CardData
from .validate_form import ValidateForm

mask_private = 'mask_private'

def textbox_entry_allowed(question):
        found = False
        answers = Answer.objects.filter(question=question)
        if question.params is not None and 'textbox' in question.params:
            found = True
        else:
            for answer in answers:
                if answer.params is not None and 'textbox' in answer.params:
                    found = True
                    break
        
        return found

def is_private_value(question, match_value):
    if question.params is not None and match_value in question.params and question.params[match_value] == 'private':
        return True
    else:
        return False

def private_mask(context, value):
    question = context['question']
    if mask_private in context and context[mask_private] == True and is_private_value(question, 'value'):
        return None
    else:
        return value
        
class ResponseStringSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['value'] = private_mask(self.context, serializers.CharField().to_representation(instance))
        return ret
    
    def to_internal_value(self, data):
        value = data.get('value')
        
        return {
            'value':value
            }
    
    def get_or_create(self):
        return self.validated_data.get('value')
    
class ResponseIntegerSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['value'] = private_mask(self.context, serializers.IntegerField().to_representation(instance))
        return ret
    
    def to_internal_value(self, data):
        value = data.get('value')
        if value is not None:
            value = int(value)
        
        return {
            'value':value
            }
    
    def get_or_create(self):
        return self.validated_data.get('value')
 
class ResponseFloatSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['value'] = private_mask(self.context, serializers.FloatField().to_representation(instance))
        return ret
 
    def to_internal_value(self, data):
        value = data.get('value')
        if value is not None:
            value = float(value)
        
        return {
            'value':value
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')
        
class ResponseRadioButtonSerializer(serializers.Serializer):
    def to_representation(self, instance):
        question = self.context['question']
        ret = super().to_representation(instance)
        if instance is not None:
            try:
                answer = Answer.objects.get(question=question, code=instance)
                value = answer.value
            except ObjectDoesNotExist:
                value = instance
        else:
            value = None
        
        ret['value'] = private_mask(self.context, serializers.CharField().to_representation(value))
        return ret
    
    def to_internal_value(self, data):
        question = self.context['question']
        value = data.get('value')
        if value is not None:
            try:
                answer = Answer.objects.get(question=question, value=value)
                if answer.code is not None:
                    value = answer.code
            except ObjectDoesNotExist:
                # value could not be found in the set of answers, but may be text box entry
                # check if text box entry is allowed for this question
                if not textbox_entry_allowed(question):
                    raise serializers.ValidationError(
                        str(question.id) + ':RadioButton value "' + value + '" does not match any answers'
                        )
        
        return {
            'value':value
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')
 
class ResponseDropdownSerializer(serializers.Serializer):
    def to_representation(self, instance):
        question = self.context['question']
        ret = super().to_representation(instance)
        if instance is not None:
            try:
                answer = Answer.objects.get(question=question, code=instance)
                value = answer.value
            except ObjectDoesNotExist:
                value = instance
        else:
            value = None
        
        ret['value'] = private_mask(self.context, serializers.CharField().to_representation(value))
        return ret

    def to_internal_value(self, data):
        question = self.context['question']
        value = data.get('value')
        if value is not None:
            try:
                answer = Answer.objects.get(question=question, value=value)
                if answer.code is not None:
                    value = answer.code
            except ObjectDoesNotExist:
                # value could not be found in the set of answers, but may be text box entry
                # check if text box entry is allowed for this question
                if not textbox_entry_allowed(question):
                    raise serializers.ValidationError(
                        str(question.id) + ':Dropdown value "' + value + '" does not match any answers'
                        )
        
        return {
            'value':value
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')
 
class ResponseCheckboxSerializer(serializers.Serializer):
    def to_representation(self, instance):
        question = self.context['question']
        ret = super().to_representation(instance)
        if textbox_entry_allowed(question):
            ret['value'] = private_mask(self.context, serializers.CharField().to_representation(instance))
        else:
            ret['value'] = private_mask(self.context, serializers.BooleanField().to_representation(instance))
        return ret
    
    def to_internal_value(self, data):
        question = self.context['question']
        return_as_string = self.context.get('return_as_string')
        value = data.get('value')
        
        return {
            'value': value
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')

class ResponseAddressSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

class ResponseAddress1Serializer(ResponseAddressSerializer):
    def get_or_create(self):
        question = self.context['question']
        id = self.validated_data.get('id')
        name = self.validated_data.get('name')
        if id is None:
            if name is not None:
                address = Address1()
                address.name = name
                address.save()
            else:
                address = None
        else:
            try:
                address = Address1.objects.get(id=int(id))
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                        str(question.id) + ':Address1 id ' + id + ' does not exist'
                        )
        
        return address
    
class ResponseAddress2Serializer(ResponseAddressSerializer):
    def get_or_create(self):
        question = self.context['question']
        address1 = self.context['address1']
        id = self.validated_data.get('id')
        name = self.validated_data.get('name')
        if id is None:
            if name is not None:
                if address1 is not None:
                    address = Address2()
                    address.name = name
                    address.address1 = address1
                    address.save()
                else:
                    raise serializers.ValidationError(
                            str(question.id) + ':Attempting to create Address2, but no Address1 provided'
                            )
            else:
                address = None
        else:
            try:
                address = Address2.objects.get(id=int(id))
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                        str(question.id) + ':Address2 id ' + id + ' does not exist'
                        )
        
        return address

 
class ResponseAddressPairSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance is not None:
            question = self.context['question']
            if mask_private in self.context and self.context[mask_private] == True and question.params is not None:
                private_data = True
            else:
                private_data = False
            if private_data and is_private_value(question, 'address1'):
                ret['address1'] = None
            else:
                tmp = ResponseAddressSerializer(instance.address1)
                ret['address1'] = tmp.data
            if private_data and is_private_value(question, 'address2'):
                ret['address2'] = None
            else:
                tmp = ResponseAddressSerializer(instance.address2)
                ret['address2'] = tmp.data
            
        return ret
    
    def to_internal_value(self, data):
        question = self.context['question']
        address1_data = data.get('address1')
        if address1_data is not None:
            self.address1_serializer = ResponseAddress1Serializer(data=address1_data, context=dict(self.context))
            self.address1_serializer.is_valid()
            address1 = self.address1_serializer.validated_data
        else:
            address1 = None
        
        address2_data = data.get('address2')
        if address2_data is not None:
            self.address2_serializer = ResponseAddress1Serializer(data=address2_data, context=dict(self.context))
            self.address2_serializer.is_valid()
            address2 = self.address2_serializer.validated_data
        else:
            address2 = None
        
        return {
            'address1':address1,
            'address2':address2
            }
        
    def get_or_create(self):
        address1_vd = self.validated_data.get('address1')
        address2_vd = self.validated_data.get('address2')
        
        if address1_vd is not None and address2_vd is not None:
            address1 = self.address1_serializer.get_or_create()
            self.address2_serializer.context['address1'] = address1
            
            address2 = self.address2_serializer.get_or_create()
        else:
            address2 = None
        
        return address2
 
class ResponsePhoneSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['value'] = private_mask(self.context, serializers.CharField().to_representation(instance))
        return ret
    
    def to_internal_value(self, data):
        value = data.get('value')
        if value is not None:
            value = int(value)
        
        return {
            'value':value
            }
    
    def get_or_create(self):
        return self.validated_data.get('value')
 
class ResponseDateSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['value'] = private_mask(self.context, serializers.DateField().to_representation(instance))
        return ret
    
    def to_internal_value(self, data):
        value = data.get('value')
        if value is not None:
            dt = parser.parse(value).date()
        else:
            dt = None
            
        return {
            'value':dt
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')
 
class ResponseDateTimeSerializer(serializers.Serializer):
    def to_representation(self, instance):
        #ret = super().to_representation(instance)
        #naive = private_mask(self.context, serializers.DateTimeField().to_representation(instance))
        ret = {}
        if instance is not None:
            time_zone = self.context['time_zone']
            tz = pytz.timezone(time_zone)
            date_time = instance.astimezone(tz)
            ret['value'] = str(date_time.replace(tzinfo=None))
        else:
             ret['value']= None
        return ret
    
    def to_internal_value(self, data):
        value = data.get('value')
        if value is not None:
            local_time = parser.parse(value)
            local_time = local_time.replace(tzinfo=None)
            time_zone = self.context['time_zone']
            tz = pytz.timezone(time_zone)
            dt = tz.localize(local_time) 
        else:
            dt = None
        return {
            'value':dt
            }
        
    def get_or_create(self):
        return self.validated_data.get('value')

class ResponseImageSerializer(serializers.Serializer):
    def to_representation(self, instance):
        question = self.context['question']
        if mask_private in self.context and self.context[mask_private] == True and is_private_value(question, 'value'): 
            ret = super().to_representation(instance)
            ret['value'] = None
        else:
            ret = super().to_representation(instance)
            ret['value'] = settings.MEDIA_URL + instance.name
        
        return ret
    
    def to_internal_value(self, data):
        question = self.context['question']
        if question.params is not None and 'subdirectory' in question.params:
            subdirectory = question.params['subdirectory']
        else:
            subdirectory = ''
        if isinstance(data,dict) and 'value' in data and isinstance(data['value'],dict) and 'name' in data['value']:
            self.image_name = subdirectory + data['value']['name']
        else:
            
            self.image_name = None
        
        return {}
    
    def get_or_create(self):
        if self.image_name is not None:
            return self.image_name
        else:
            form_data = self.context['form_data']
            question = self.context['question']
            return form_data.get_answer(question)
        
        
    
class ResponsePersonSerializer(serializers.Serializer):     
    def to_representation(self, instance):
        question = self.context['question']
        if mask_private in self.context and self.context[mask_private] == True and question.params is not None:
            private_data = True
        else:
            private_data = False
        ret = super().to_representation(instance)
        if instance is not None:
            ret['storage_id'] = serializers.IntegerField().to_representation(instance.id)
            if private_data and is_private_value(question, 'name'):
                ret['name'] = None
            else:
                tmp = ResponseStringSerializer(instance.full_name, context=self.context)
                ret['name'] = tmp.data
            if private_data and is_private_value(question, 'address1'):
                ret['address1'] = None
            else:
                tmp = ResponseAddressSerializer(instance.address1, context=self.context)
                ret['address1'] = tmp.data
            if private_data and is_private_value(question, 'address2'):
                ret['address2'] = None
            else:
                tmp = ResponseAddressSerializer(instance.address2, context=self.context)
                ret['address2'] = tmp.data
            if private_data and is_private_value(question, 'phone'):
                ret['phone'] = None
            else:
                tmp = ResponseStringSerializer(instance.phone_contact, context=self.context)
                ret['phone'] = tmp.data
            if private_data and is_private_value(question, 'gender'):
                ret['gender'] = None
            else:
                if instance.gender == 'F':
                    gender = 'Female'
                elif instance.gender == 'M':
                    gender = 'Male'
                else:
                    gender = 'Unknown'    
                tmp = ResponseStringSerializer(gender, context=self.context)
                ret['gender'] = tmp.data
            if private_data and is_private_value(question, 'age'):
                ret['age'] = None
            else:
                tmp = ResponseIntegerSerializer(instance.age, context=self.context)
                ret['age'] = tmp.data
            if private_data and is_private_value(question, 'birthdate'):
                ret['birthdate'] = None
            else:
                tmp = ResponseDateSerializer(instance.birthdate, context=self.context)
                ret['birthdate'] = tmp.data
            if private_data and is_private_value(question, 'passport'):
                ret['passport'] = None
            else:
                tmp = ResponseStringSerializer(instance.passport, context=self.context)
                ret['passport'] = tmp.data
            if private_data and is_private_value(question, 'nationality'):
                ret['nationality'] = None
            else:
                tmp = ResponseStringSerializer(instance.nationality, context=self.context)
                ret['nationality'] = tmp.data
            
        return ret
    
    def to_internal_value(self, data):
        ret = {}
        storage_id = data.get('storage_id')
        if storage_id is not None:
            ret['storage_id'] = int(storage_id)
        
        tmp = data.get('name')
        if tmp is not None:  
            ret['name'] = tmp.get('value')
        
        address1 = data.get('address1')
        self.address1_serializer = ResponseAddress1Serializer(data=address1, context=dict(self.context))
        self.address1_serializer.is_valid()
        address2 = data.get('address2')
        self.address2_serializer = ResponseAddress2Serializer(data=address2, context=dict(self.context))
        self.address2_serializer.is_valid()
        
        tmp = data.get('phone')
        if tmp is not None and tmp.get('value') is not None:
            ret['phone'] = tmp.get('value')
        else:
            ret['phone'] = ''
        
        tmp = data.get('gender')
        if tmp is not None:
            gender = tmp.get('value')
            if gender.upper() == 'FEMALE':
                ret['gender'] = 'F'
            elif gender.upper() == 'MALE':
                ret['gender'] = 'M'
            else:
                ret['gender'] = 'U'
        
        tmp = data.get('age')
        if tmp is not None:
            age = tmp.get('value')
            if age is not None:
                ret['age'] = int(age)
                
        tmp = data.get('birthdate')
        if tmp is not None:          
            birthdate = tmp.get('value')
            if birthdate is not None:
                ret['birthdate'] = parser.parse(birthdate).date()
                         
        tmp = data.get('passport')
        if tmp is not None and tmp.get('value') is not None:
            ret['passport'] = tmp.get('value')
        else:
            ret['passport'] = ''
            
        tmp = data.get('nationality')
        if tmp is not None and tmp.get('value') is not None:
            ret['nationality'] = tmp.get('value')
        else:
            ret['nationality'] = ''
        
        return ret
    
    def match_address(self, address_object1, address_object2):
        match = True
        if (address_object1 is None and address_object2 is not None or
            address_object1 is not None and address_object2 is None):
            match = False
        elif address_object1 is not None and address_object2 is not None:
            if address_object1.id != address_object2.id:
                match = False
        
        return match
            

    def get_or_create(self):
        mode = self.context.get('mode')
        storage_id = self.validated_data.get('storage_id')
        name = self.validated_data.get('name')
        address1 = self.address1_serializer.get_or_create()
        self.address2_serializer.context['address1'] = address1
        address2 = self.address2_serializer.get_or_create()
        phone = self.validated_data.get('phone')
        gender = self.validated_data.get('gender')
        age = self.validated_data.get('age')
        birthdate = self.validated_data.get('birthdate')
        passport = self.validated_data.get('passport')
        nationality = self.validated_data.get('nationality')
        
        update_data = False
        if storage_id is None:
            person = Person()
            update_data = True
        else:
            person = Person.objects.get(id=storage_id)
            if (
                person.full_name != name or
                not self.match_address(person.address1, address1) or
                not self.match_address(person.address2, address2) or
                person.phone_contact != phone or
                person.gender != gender or
                person.age != age or
                person.birthdate != birthdate or
                person.passport != passport or
                person.nationality != nationality):
                update_data = True
                if mode != 'IRF':
                    person = Person()
        
        if update_data:
            person.full_name = name
            person.address1 = self.address1_serializer.get_or_create()
            self.address2_serializer.context['address1'] = address1
            person.address2 = self.address2_serializer.get_or_create()
            person.phone_contact = phone
            person.gender = gender
            person.age = age
            person.birthdate = birthdate
            person.passport = passport
            person.nationality = nationality
            person.save()
        
        return person 
        
class QuestionResponseSerializer(serializers.Serializer):    
    answer_type_to_serializer = {
        'String':ResponseStringSerializer,
        'Integer':ResponseIntegerSerializer,
        'Float':ResponseFloatSerializer,
        'RadioButton':ResponseRadioButtonSerializer,
        'Dropdown':ResponseDropdownSerializer,
        'Checkbox':ResponseCheckboxSerializer,
        'Address':ResponseAddressPairSerializer,
        'Phone':ResponsePhoneSerializer,
        'Date':ResponseDateSerializer,
        'DateTime':ResponseDateTimeSerializer,
        'Image':ResponseImageSerializer,
        'Person':ResponsePersonSerializer,
        }
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        form_data = self.context['form_data']
        
        answer = form_data.get_answer(instance)
        ret['question_id']  = serializers.IntegerField().to_representation(instance.id)
        if form_data.get_answer_storage(instance) is not None:
            ret['storage_id'] = serializers.IntegerField().to_representation(form_data.get_answer_storage(instance))
        if answer is not None:
            serializer = self.answer_type_to_serializer[instance.answer_type.name](answer, context=self.context)
            ret['response'] = serializer.data
        else:
            ret['response'] = {'value':None}
        
        return ret
    
    def to_internal_value(self, data):
        question_id = data.get('question_id')
        question = Question.objects.get(id=int(question_id))
        storage_id = data.get('storage_id')
        if storage_id is not None:
            storage_id = int(storage_id)
        answer = data.get('response')
        context=dict(self.context)
        context['question'] = question
        self.response_serializer = self.answer_type_to_serializer[question.answer_type.name](data=answer, context=context)
        self.response_serializer.is_valid()
        return {
            'question': question,
            'storage_id': storage_id,
            'response': self.response_serializer.validated_data
            }
        
    def get_or_create(self):
        form_data = self.context['form_data']
        self.response_serializer.is_valid()
        question = self.validated_data.get('question')
        storage_id = self.validated_data.get('storage_id')
        self.response_serializer.context['form_data'] = form_data
        response = self.response_serializer.get_or_create()
        
        form_data.set_answer(question, response, storage_id)
        return response

class QuestionLayoutSerializer(serializers.Serializer):
    def to_representation(self, instance):
        context = dict(self.context)
        context['question'] = instance.question
        serializer = QuestionResponseSerializer(instance.question, context=context)
        return serializer.data
    
    def to_internal_value(self, data):
        self.layout_serializer = QuestionResponseSerializer(data=data, context=dict(self.context))
        self.layout_serializer.is_valid()
        return self.layout_serializer.validated_data
    
    def get_or_create(self):
        self.layout_serializer.context['form_data'] = self.context['form_data']
        return self.layout_serializer.get_or_create()
        

class CardSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.form_object.id is not None:
            ret['storage_id'] = serializers.IntegerField().to_representation(instance.form_object.id)
        category = self.context['category']
        question_layouts = QuestionLayout.objects.filter(category__form = instance.form_data.form, category=category).order_by('question__id')
        context = dict(self.context)
        context['form_data'] = instance
        serializer = QuestionLayoutSerializer(question_layouts, many=True, context=context)
        ret['responses'] = serializer.data
        return ret
    
    def to_internal_value(self, data):
        tmp = data.get('storage_id')
        if tmp is not None:
            storage_id = int(tmp)
        else:
            storage_id = None
        
        responses = data.get('responses')
        self.response_serializers = []
        for response in responses:
            context = dict(self.context)
            serializer = QuestionLayoutSerializer(data=response, context=context)
            serializer.is_valid()
            self.response_serializers.append(serializer)
        
        return {
            'storage_id':storage_id
            }
    
    def get_or_create(self):
        category = self.context['category']
        form_data = self.context['form_data']
        
        storage_id = self.validated_data.get('storage_id')
        blank_id = self.context.get('clear_storage_id')
        if blank_id is not None:
            storage_id = None
            
        if storage_id is None:
            card_object = form_data.category_form_dict[category.id].form_model()
            card = CardData(card_object, form_data.category_form_dict[category.id], response_dict={})
            card.form_data = form_data
            form_data.card_dict[category.id].append(card)
        else:
            card = form_data.find_card(category, storage_id)
            card.is_valid = True
        
        for serializer in self.response_serializers:
            serializer.context['form_data'] = card
            serializer.get_or_create()
        

class CardCategorySerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['category_id'] = serializers.IntegerField().to_representation(instance.id)
        context = dict(self.context)
        context['category'] = instance
        form_data = context['form_data']
        if instance.id in form_data.card_dict:
            serializer = CardSerializer(form_data.card_dict[instance.id], many=True, context=context)
        else:
            serializer = CardSerializer(None, many=True)
        ret['instances'] = serializer.data
        
        return ret
    
    def to_internal_value (self, data):
        tmp = data.get('category_id')
        category_id = serializers.IntegerField().to_internal_value(tmp)
        category = Category.objects.get(id=category_id)
        
        instances = data.get('instances')
        self.card_instance_serializers = []
        ret = []
        for instance in instances:
            context = dict(self.context)
            context['category'] = category
            serializer = CardSerializer(data=instance, context=context)
            serializer.is_valid()
            #ret.append(serializer.data)
            self.card_instance_serializers.append(serializer)
        
        return ret
        
    def get_or_create(self):
        form_data = self.context.get('form_data')
        for serializer in self.card_instance_serializers:
            serializer.context['form_data'] = form_data
            serializer.get_or_create()
        

class FormDataSerializer(serializers.Serializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['station_id'] = serializers.IntegerField().to_representation(instance.form_object.station.id)
        ret['country_id'] = serializers.IntegerField().to_representation(instance.form_object.station.operating_country.id)
        ret['status'] = serializers.CharField().to_representation(instance.form_object.status)
        if instance.form_object.id is not None:
            ret['storage_id'] = serializers.IntegerField().to_representation(instance.form_object.id)
        if self.context is not None:
            context = dict(self.context)
        else:
            context = {}
        
        question_layouts = QuestionLayout.objects.filter(category__form = instance.form).exclude(category__category_type__name = 'card').order_by('question__id')
        context['form_data'] = instance
        context['time_zone'] = instance.form_object.station.time_zone
        serializer = QuestionLayoutSerializer(question_layouts, many=True, context=context)
        ret['responses'] = serializer.data
        
        card_types = Category.objects.filter(form = instance.form, category_type__name = 'card')
        serializer = CardCategorySerializer(list(card_types), many=True, context=context)
        ret['cards'] = serializer.data
        
        return ret
    
    def to_internal_value(self, data):
        self.the_errors = []
        self.the_warnings = []
        tmp = data.get('station_id')
        station_id = serializers.IntegerField().to_internal_value(tmp)
        tmp = data.get('country_id')
        country_id = serializers.IntegerField().to_internal_value(tmp)
        status = data.get('status')
        tmp = data.get('ignore_warnings')
        if tmp is not None and tmp.upper() == 'TRUE':
            ignore_warnings = True
        else:
            ignore_warnings = False
            
        tmp = data.get('storage_id', None)
        if self.instance is None and tmp is not None:
            self.the_errors = ["storage_id for form specified on create",]
            self.the_warnings = []
            raise serializers.ValidationError("storage_id for form specified on create");
        
        station = BorderStation.objects.get(id=station_id)
        self.context['time_zone'] = station.time_zone
        
        if tmp is None:
            storage_id = None
        else:
            storage_id = serializers.IntegerField().to_internal_value(tmp)       
        
        responses = data.get('responses')
        responses_data = []
        self.form_serializers = []
        for response in responses:
            serializer = QuestionLayoutSerializer(data=response, context=dict(self.context))
            serializer.is_valid()
            self.form_serializers.append(serializer)
        
        self.card_serializers = []
        cards = data.get('cards')
        for card in cards:
            serializer = CardCategorySerializer(data=card, context=dict(self.context))
            serializer.is_valid()
            self.card_serializers.append(serializer)
        
        form_type = self.context.get('form_type')
        form = Form.current_form(form_type.name, country_id)
        if self.instance is None:
            form_class = form.find_form_class()
            form_object = form_class()
            form_object.station = station
            form_data = FormData(form_object, form)
            request_user = self.context.get('request.user')
            form_data.form_object.form_entered_by = request_user
        else:
            form_data = self.instance
            for card_list in form_data.card_dict.values():
                for card in card_list:
                    card.invalidate_card()
        
        form_data.form_object.status = status
        for serializer in self.form_serializers:
            serializer.context['form_data'] = form_data
            serializer.get_or_create()
        
        for serializer in self.card_serializers:
            serializer.context['form_data'] = form_data
            serializer.get_or_create()
        
        self.form_data = form_data
        
        self.validate_form(form, form_data, ignore_warnings)
             
        return {
            'station_id':station_id,
            'country_id': country_id,
            'status': status,
            }
    
    def get_country_id(self):
        if self.form_data is None or self.form_data.form_object is None or self.form_data.form_object.station is None or self.form_data.form_object.station.operating_country is None:
            return None
        else:
            return self.form_data.form_object.station.operating_country.id
    
    def get_station_id(self):
        if self.form_data is None or self.form_data.form_object is None or self.form_data.form_object.station is None:
            return None
        else:
            return self.form_data.form_object.station.id
        
    def validate_form(self, form, form_data, ignore_warnings):
        validate = ValidateForm(form, form_data, ignore_warnings)
        validate.validate()
        self.the_errors = self.the_errors + validate.errors
        self.the_warnings = self.the_warnings + validate.warnings
        if len(validate.errors) > 0:
            raise serializers.ValidationError(validate.errors[0])
        elif len(validate.warnings) > 0:
            raise serializers.ValidationError(validate.warnings[0])

    def create(self, validated_data):
        self.form_data.save()
        return self.form_data
    
    def update(self, instance, validated_data):
        self.form_data.save()
        
        return self.form_data