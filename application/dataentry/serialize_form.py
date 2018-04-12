import logging
import traceback

from datetime import date
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

from .models.form import Answer, CardStorage, Category, Form, Question, QuestionLayout, QuestionStorage, Storage
from .models.border_station import BorderStation
from .models.addresses import Address1, Address2
from .models.person import Person
from .form_data import FormData, CardData


logger = logging.getLogger(__name__);

class SerializeForm:
    def __init__(self):
        self.response_code = status.HTTP_200_OK
        self.detail = []
        
    def person_serialize(self, question, field_value=None, response_value=None):
        if field_value is not None:
            person = field_value
        elif response_value is not None:
            try:
                person = Person.objects.get(id=int(response_value))
            except ObjectDoesNotExist:
                logger.error('person for question ' + str(question.id) + ' is not found')
                self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                person = None
        else:
            person = None
        
        if person is not None:
            data = {}
            data['storage_id'] = person.id
            data['name'] = { 'value': person.full_name }
            if person.address2 is not None:
                data['address1'] = {
                        'id': person.address2.address1.id,
                        'value': person.address2.address1.name
                    }
                data['address2'] = {
                        'id': person.address2.id,
                        'value': person.address2.name
                    }
            if person.phone_contact is not None:
                data['phone'] = {'value': person.phone_contact }
                
            if person.gender == 'M':
                data['gender'] = {'value': 'Male' }
            elif person.gender == 'F':
                data['gender'] = {'value': 'Female' }
            else:
                data['gender'] = {'value': 'Unknown' }
            
            if person.age is not None:
                data['age'] = {'value': person.age }
            
            return data
        else:
            return None
      
    def address_serialize(self, question, field_value=None, response_value=None):
        if field_value is not None:
           address2 = field_value
        elif response_value is not None:
            try:
                address2 = Address2.objects.get(id=int(response_value))
            except ObjectDoesNotExist:
                logger.error('address2 for question ' + str(question.id) + ' is not found')
                self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                address2 = None
        else:
            address2 = None
        
        if address2 is not None:
            addr1 = {}
            addr1['id'] = address2.address1.id
            addr1['value'] = address2.address1.name
            
            addr2 = {}
            addr2['id'] = address2.id
            addr2['value'] = address2.name
            
            return {'address1':addr1, 'address2': addr2}
        else:
            return None
             
    def radiobutton_serialize(self, question, field_value=None, response_value=None):
        data = {}
        
        if field_value is not None:
            code = field_value
        elif response_value is not None:
            code = rsponse_value
        else:
            code = None
        
        if code is not None:
            try:
                answer = Answer.objects.get(question=question, code=code)
                val = { "value": answer.value }
            except ObjectDoesNotExist:
                val = { "value": code }
        else:
            val = None
        
        return val
       
    def dropdown_serialize(self, question, field_value=None, response_value=None):
        data = {}
        
        if field_value is not None:
            code = field_value
        elif response_value is not None:
            code = rsponse_value
        else:
            code =  None
        
        if code is not None:
            try:
                answer = Answer.objects.get(question=question, code=code)
                val = { "value": answer.value }
            except ObjectDoesNotExist:
                val = { "value": code }
        else:
            val = None
        
        return val
    
    def checkbox_serialize(self, question, field_value=None, response_value=None):
        if field_value is not None:
            if isinstance(field_value, bool):
                if field_value == True:
                    val = 'True'
                elif field_value == False:
                    val = 'False'
            else:
                val = field_value
        elif response_value is not None:
            val = response_value
        else:
            val = None
        
        if val is not None:
            return {'value': val }
        else:
            return None
    
    def date_time_serialize(self, question, field_value=None, response_value=None):
        if field_value is not None:
            val = str(field_value)
        elif response_value is not None:
            val = rsponse_value
        else:
            val = None
        
        if val is not None:
            return {'value': val }
        else:
            return None 
    
    def image_serialize(self, question, field_value=None, response_value=None):
        if field_value is not None:
            val = str(field_value)
        elif response_value is not None:
            val = response_value
        else:
            val = None
        
        if val is not None:
            return {'value':val}
        else:
            return None
            
    question_serialization_method = {
        'Person': person_serialize,
        'Address': address_serialize,
        'RadioButton': radiobutton_serialize,
        'Checkbox': checkbox_serialize,
        'Dropdown': dropdown_serialize,
        'DateTime': date_time_serialize,
        'Image': image_serialize
    }
                
    def serializeResponses(self, question_layouts, form_data):
        question_list = []
        object = form_data.form_object
        for question_layout in question_layouts:
            question = question_layout.question
            question_data = { 'question_id': question.id }
            
            tmp_val = form_data.get_answer(question)
            storage = form_data.get_answer_storage(question)
            if tmp_val is not None:
                if question.answer_type.name in self.question_serialization_method:
                    if form_data.in_form_object(question):
                        val = self.question_serialization_method[question.answer_type.name](self,question, field_value=tmp_val)
                    else:
                        val = self.question_serialization_method[question.answer_type.name](self,question, response_value=tmp_val)   
                else:
                    val = { "value": tmp_val }
            else:
                val = None
            
            if val is not None:
                question_data['response']  = val
                if storage is not None:
                    question_data['storage_id'] = storage
                question_list.append(question_data)
                
        return question_list
    
    # Serialize category that is not of type card
    def serializeCategory(self, form_data, category):
        question_layouts = QuestionLayout.objects.filter(category=category)
        return self.serializeResponses(question_layouts, form_data)
    
    # Serialize all cards for a given category
    def serialize_cards(self, form_data, category):
        question_layouts = QuestionLayout.objects.filter(category=category)
        
        card_data = {
            'category_id': category.id
        }
        instance_list = []
        
        cards = form_data.card_dict[category.id]
        for card in cards:
            data = {"storage_id": card.form_object.id}
            data['responses'] = self.serializeResponses(question_layouts, card)
            instance_list.append(data)
        
        card_data['instances'] = instance_list
        return card_data

    
    def serialize(self, form_data):
        object = form_data.form_object
        response_model = form_data.response_model
            
        form_dict = {}
        form_dict['form_id'] = object.id
        form_dict['station_id'] = object.station.id
        form_dict['country_id'] = object.station.operating_country.id
        form_dict['status'] = object.status
        
        form_dict['storage_id'] = object.id
        
        categories = Category.objects.filter(form = form_data.form)
       
        response_list = []
        card_list = []
        for category in categories:
            if category.category_type.name == 'card':
                try:
                    card_list.append(self.serialize_cards(form_data, category))
                except Exception as e:
                    logger.error('Failed to serialize cards for category ' + category.name + ' ' + traceback.format_exc())
                    self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            else:
                try:
                    response_list = response_list + self.serializeCategory(form_data, category)
                except Exception as e:
                    logger.error('Failed to serialize responses for category ' + category.name + ' ' + traceback.format_exc())
                    self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                
        form_dict['responses'] = response_list
        form_dict['cards'] = card_list
        
        return form_dict
    

    def person_deserialize(self, response, question, return_as_string, mode):
        storage_id = response.get('storage_id')
        tmp = response.get('name')
        if tmp is not None:
            name = tmp.get('value')
        else:
            name = None
            
        tmp = response.get('phone')
        if tmp is not None:
            phone = tmp.get('value')
        else:
            phone = None
            
        tmp = response.get('gender')
        if tmp is not None:
            gender = tmp.get('value')
        else:
            gender = 'Unknown'
        if gender == 'Female':
            gender_code = 'F'
        elif gender == 'Male':
            gender_code = 'M'
        else:
            gender_code = 'U'
            
        tmp = response.get('age')
        if tmp is not None:
            age = tmp.get('value')
        else:
            age = None
        
        address1_dict = response.get('address1')
        address2_dict = response.get('address2')
        
        if address1_dict is not None and address2_dict is not None:
            address1_id = address1_dict.get('id')
            if address1_id is None:
                address_name = address1_dict.get('value')
                try:
                    # check for an existing address1 with the same name
                    address1 = Address1.objects.get(name=address_name)
                except ObjectDoesNotExist:
                    address1 = Address1()
                    address1.name = address_name
                    address1.save()
            else:
                address1 = Address1.objects.get(id=address1_id)
            
            address2_id = address2_dict.get('id')
            if address2_id is None:
                address_name = address2_dict.get('value')
                try:
                    address2 = Address2.get(address1=address1, name=address_name)
                except ObjectDoesNotExist:
                    address2 = Address2()
                    address2.address1 = address1
                    address2.name = address_name
                    address2.save()
            else:
                address2 = Address2.objects.get(id = address2_id)
        
        
        if storage_id is None:
            person = Person()
            person.address1 = address1
            person.address2 = address2
            person.full_name = name
            person.phone = phone
            person.gender = gender_code
            person.age = age
            person.save()
        else:
            person = Person.objects.get(id=storage_id)
            # person object may only be modified in IRF mode
            # create new person object if changes and not in IRF mode
            if mode != 'IRF' and (
                    person.address1 != address1 or
                    person.address2 != address2 or
                    person.name != name or
                    person.phone != phone or
                    person.gender != gender_code or
                    person.age != age):
                person = Person()
                
            person.address1 = address1
            person.address2 = address2
            person.name = name
            person.phone = phone
            person.gender = gender_code
            person.age = age
            person.save()
            
        if return_as_string:
            return str(person.id)
            
        return person  
    
    def address_deserialize(self, response, question, return_as_string, mode):
        address1_dict = response.get('address1')
        address2_dict = response.get('address2')
        
        if address1_dict is not None and address2_dict is not None:
            address1_id = address1_dict.get('id')
            if address1_id is None:
                address_name = address1_dict.get('name')
                try:
                    # check for an existing address1 with the same name
                    address1 = Address1.objects.get(name=address_name)
                except ObjectDoesNotExist:
                    address1 = Address1()
                    address1.name = address_name
                    address1.save()
            else:
                address1 = Address1.objects.get(id=address1_id)
            
            address2_id = address2_dict.get('id')
            if address2_id is None:
                address_name = address2_dict.get('name')
                try:
                    address2 = Address2.get(address1=address1, name=address_name)
                except ObjectDoesNotExist:
                    address2 = Address2()
                    address2.address1 = address1
                    address2.name = address_name
                    address2.save()
            else:
                address2 = Address2.get(id = address2_id)
        else:
            address2 = None
        
        if return_as_string:
            return str(address2.id)
        
        return address2
    
    def textbox_entry_allowed(self, question):
        found = False
        answers = Answer.objects.filter(question=question)
        for answer in answers:
            if 'TEXTBOX' in answer.params.upper():
                found = True
                break
        
        return found
    
    def radiobutton_deserialize(self, response, question, return_as_string, mode):
        value = response.get('value')
        try:
            answer = Answer.objects.get(question=question, value=value)
            if answer.code is not None:
                value = answer.code
        except ObjectDoesNotExist:
            # value could not be found in the set of answers, but may be texbox entry
            if not self.textbox_entry_allowed(question):
                self.response_code = status.HTTP_400_BAD_REQUEST
                msg = "Unable to locate answer value " + value + " for radio button question " + str(question.id)
                logger.error(msg)
                self.detail.append(msg)
        
        return value
        
        
       
    def dropdown_deserialize(self, response, question, return_as_string, mode):
        value = response.get('value')
        try:
            answer = Answer.objects.get(question=question, value=value)
            if answer.code is not None:
                value = answer.code
        except ObjectDoesNotExist:
            # value could not be found in the set of answers, but may be texbox entry
            if not self.textbox_entry_allowed(question):
                self.response_code = status.HTTP_400_BAD_REQUEST
                msg = "Unable to locate answer value " + value + " for drop down question " + str(question.id)
                logger.error(msg)
                self.detail.append(msg)
        
        return value
    
    def checkbox_deserialize(self, response, question, return_as_string, mode):
        value = response.get('value')
        if not 'TEXTBOX' in question.params.upper():
            if not return_as_string:
                if value.upper() == 'TRUE':
                    value = True
                elif value.upper() == 'FALSE':
                    value = False
                else:
                    self.response_code = status.HTTP_400_BAD_REQUEST
                    msg = 'Checkbox value is neither True or False for question ' + str(question.id) + ' assuming False'
                    self.detail.append(msg)
                    logger.error(msg)
                    value = False
            else:
                if not (value.upper() == 'TRUE' or value.upper() == 'FALSE'):
                    self.response_code = status.HTTP_400_BAD_REQUEST
                    msg = 'Checkbox value is neither True or False for question ' + str(question.id) + ' assuming False'
                    self.detail.append(msg)
                    logger.error(msg)
                    value = 'False'
        
        return value
            
    
    question_deserialization_method = {
        'Person': person_deserialize,
        'Address': address_deserialize,
        'RadioButton': radiobutton_deserialize,
        'Dropdown': dropdown_deserialize
    }
    
    def deserialize_responses (self, responses, form, form_model_class, response_model_class, mode):
        response_object_dict = {}
        for response in responses:
            question_id = response['question_id']
            question = Question.objects.get(id=question_id)
            the_response = response.get('response')
            storage_id = response.get('storage_id')
            try:
                question_storage = QuestionStorage.objects.get(question = question)
                if question.answer_type.name in self.question_deserialization_method:
                    val = self.question_deserialization_method[question.answer_type.name](self, the_response, question, False, mode)
                else:
                    val = the_response.get('value')
                setattr(form, question_storage.field_name, val) 
            except ObjectDoesNotExist:
                if response_model_class is not None:
                    if storage_id is None:
                        response_object = response_model_class()
                        response_object.parent = form
                        response_object.question = question
                    else:
                        response_object = response_model_class.objects.get(id=storage_id)
                        
                    if question.answer_type.name in self.question_deserialization_method:
                        response_object.value = self.question_deserialization_method[question.answer_type.name](self, response, question, True, mode)
                    else:
                        response_object.value = the_response.get('value')
                        
                    response_object_dict[question_id] = response_object
                else:
                    logger.error ('Question storage is not specified and there is no response model class defined for question id=' + question_id)
                    self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        return response_object_dict
    
    def deserialize_cards (self, cards, form, mode):
        card_dict = {}
        for card in cards:
            category_id = card['category_id']
            card_storage = CardStorage.objects.get(category__id = category_id)
            storage = Storage.objects.get(id=card_storage.storage.id)
            mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
            card_model_class = getattr(mod, storage.form_model_name)
            if storage.response_model_name is not None:
                response_model_class = getattr(mod, storage.response_model_name, None)
            else:
                response_model_class = None
            
            instance_list = card['instances']
            card_list = []
            for inst in instance_list:
                storage_id = inst.get('storage_id')
                if storage_id is None:
                    inst_object = card_model_class()
                else:
                    inst_object = card_model_class.objects.get(id=storage_id)
                
                responses = inst['responses']
                responses_to_save = self.deserialize_responses(responses, inst_object, card_model_class, response_model_class, mode)
                
                card_list.append(CardData(inst_object, card_model_class, response_model_class, response_dict = responses_to_save))
                
            card_dict[category_id] = card_list
        
        return card_dict            
    
    def deserialize(self, form_dict, mode):
        self.response_code = status.HTTP_200_OK
        self.detail = []
        
        form = Form.objects.get(id=form_dict['form_id'])
        form_status = form_dict['status']
        ignore_warnings = form_dict.get('ignore_warnings')
        if ignore_warnings is  None or ignore_warnings.upper() != 'TRUE':
            ignore_warnings = 'False'
        
        storage = Storage.objects.get(id=form.storage.id)
        mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
        form_model_class = getattr(mod, storage.form_model_name)
        response_model_class = getattr(mod, storage.response_model_name, None)
        storage_id = form_dict.get('storage_id')
        if storage_id is None:
            form_instance = form_model_class()
            station_id = form_dict['station_id']
            form_instance.station = BorderStation.objects.get(id=station_id)
        else:
            form_instance = form_model_class.objects.get(id=storage_id)
            
        form_instance.status = form_status
        
        responses = form_dict['responses']
        responses_to_save = self.deserialize_responses(responses, form_instance, form_model_class, response_model_class, mode)
        
        cards = form_dict['cards']
        cards_to_save = self.deserialize_cards(cards, form, mode)
        
        object_to_save = {"form": form_instance, "responses": responses_to_save, "cards": cards_to_save, "ignore_warnings": ignore_warnings }
        
        form_data = FormData(form_instance, response_dict = responses_to_save, card_dict = cards_to_save, response_model=response_model_class, form=form)
        
        return form_data
    
    def find_old_objects_to_remove(self, form_dict, new_object):
        objects_to_remove = []
        existing_object = self.find_existing_object(form_dict, new_object)
        if existing_object is None:
            return objects_to_remove
        
        old_responses = existing_object['responses']
        new_responses = new_object['responses']
        for old_response in old_responses:
            found = False
            for new_response in new_responses:
                if old_response.id == new_response.id:
                    found = True
                    break
            
            if not found:
                objects_to_remove.append(old_response)
        
        old_cards = existing_object['cards']
        new_cards = new_object['cards']
        for old_card in old_cards:
            old_form = old_card['form']
            found_card = None
            for new_card in new_cards:
                new_form = new_card['form']
                if type(old_form) == type(new_form) and old_form.id == new_form.id:
                    found_card = new_card
                    break
            
            if found_card is None:
                objects_to_remove.append(old_form)
                objects_to_remove += old_card['responses']
            else:
                old_responses = old_card['responses']
                new_responses = found_card['responses']
                for old_response in old_responses:
                    found = False
                    for new_response in new_responses:
                        if old_response.id == new_response.id:
                            found = True
                            break
                    
                    if not found:
                        objects_to_remove.append(old_response)
                        
        return objects_to_remove
            
    
        
            
            