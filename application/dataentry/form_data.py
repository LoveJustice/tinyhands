from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .models.form import CardStorage, Category, Form, FormType, QuestionLayout, QuestionStorage, Storage

class CategoryForm:
    def __init__(self, category, card_class, card_response_class, foreign_key_field_parent):
        self.category = category
        self.form_model = card_class
        self.response_model = card_response_class
        self.foreign_key_field_parent = foreign_key_field_parent
        
class CardData:
    def load_responses(self):
        if self.category_form.response_model is not None:
            responses = self.category_form.response_model.objects.filter(parent = self.form_object)
            self.response_dict = {}
            for response in responses:
                self.response_dict[response.question.id] = response
        else:
            self.response_dict = {}
            
    def __init__(self, card, category_form, response_dict = None, form_data=None):
        self.form_data = form_data
        self.form_object = card
        self.category_form = category_form
        self.is_valid = True
        
        if response_dict is None:
            self.load_responses()
        else:
            self.response_dict = response_dict
    
    def invalidate_card(self):
        self.is_valid = False
    
    def in_form_object(self, question):
        return question.id in self.form_data.question_storage
            
    def get_answer(self, question):
        if self.in_form_object(question):
            answer = getattr(self.form_object, self.form_data.question_storage[question.id].field_name, None)
        else:
            if question.id in self.response_dict:
                answer = self.response_dict[question.id].value
            else:
                answer = None
        
        return answer
    
    def set_answer (self, question, answer, storage_id):
        if self.in_form_object(question):
            setattr(self.form_object, self.form_data.question_storage[question.id].field_name, answer)
        else:
            if storage_id:
                card_response = self.category_form.response_model.objects.get(id=storage_id)
                card_response.parent = self.form_data.form_object
                card_response.question = question
            else:
                card_response = self.category_form.response_model()
                
            card_response.value = answer
            
            self.response_dict[question.id] = card_response
    
    def get_answer_storage(self, question):
        if self.in_form_object(question):
            storage = self.form_object.id
        elif question.id in self.response_dict:
            storage = self.response_dict[question.id].id
        else:
            storage = None
        
        return storage
    
    def save(self):
        self.form_object.set_parent(self.form_data.form_object)
        self.form_object.save()
        for response in self.response_dict.values():
            response.parent = self.form_object
            response.save()
    
    def delete(self):
        for response in self.response_dict.values():
            response.delete()
            
        self.form_object.delete()
        

class FormData:
    def load_responses(self):
        if self.response_model is not None:
            responses = self.response_model.objects.filter(parent = self.form_object)
            self.response_dict = {}
            for response in responses:
                self.response_dict[response.question.id] = response
        else:
            self.response_dict = {}
            
    def load_cards(self, category, object):
        card_list = []
        category_form = self.category_form_dict[category.id]
        
        cards = eval('category_form.form_model.objects.filter(' + category_form.foreign_key_field_parent + '__id=object.id)')
        for card in cards:
            card_list.append(CardData(card, category_form, form_data=self))
        
        return card_list
    
    def load_question_storage(self, form):
        self.question_storage = {}
        question_ids = list(QuestionLayout.objects.filter(category__form = form).values_list('question_id', flat=True))
        question_storage_list = QuestionStorage.objects.filter(question__id__in=question_ids)
        for question_storage in question_storage_list:
            self.question_storage[question_storage.question.id] = question_storage
            
    
    def __init__(self, object, form):
        self.form = form
        self.form_object = object
        self.form_model = object.__class__
        storage = Storage.objects.get(form_model_name = object.__class__.__name__)
        if storage.response_model_name is not None:
            mod = __import__(storage.module_name, fromlist=[storage.response_model_name])
            self.response_model = getattr(mod, storage.response_model_name, None)
            if self.response_model is None:
                logger.error("Unable to resolve response model")
                self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            self.response_model = None
        
        self.load_question_storage(form)
        
        self.response_dict = {}
        if object.id is not None:
            self.load_responses()
            
        self.card_dict = {}
        self.category_form_dict = {}
        categories = Category.objects.filter(form = self.form, category_type__name = 'card')
        for category in categories:
            card_storage = CardStorage.objects.get(category=category)
            mod = __import__(card_storage.storage.module_name, fromlist=[card_storage.storage.form_model_name, card_storage.storage.response_model_name])
            card_model = getattr(mod, card_storage.storage.form_model_name, None)
            if card_storage.storage.response_model_name is not None:
                card_response_model = getattr(mod, card_storage.storage.response_model_name, None)
            else:
                card_response_model = None
            category_form = CategoryForm(category, card_model, card_response_model, card_storage.storage.foreign_key_field_parent)
            self.category_form_dict[category.id] = category_form
            if object.id is None:
                self.card_dict[category.id] = []
            else:
                card_list = self.load_cards(category, object)
                self.card_dict[category.id] = card_list
                
    def find_card(self, category, id):
        ret = None
        card_list = self.card_dict[category.id]
        for card in card_list:
            if card.form_object.id == id:
                ret = card
                break
        
        return ret
        
    
    def in_form_object(self, question):
        return question.id in self.question_storage
    
    def get_answer(self, question):
        if self.in_form_object(question):
            answer = getattr(self.form_object, self.question_storage[question.id].field_name, None)
        else:
            if question.id in self.response_dict:
                answer = self.response_dict[question.id].value
            else:
                answer = None
        
        return answer
    
    def set_answer (self, question, answer, storage_id):
        if self.in_form_object(question):
            setattr(self.form_object, self.question_storage[question.id].field_name, answer)
        else:
            if question.id in self.response_dict:
                self.response_dict[question.id].value = answer
                self.response_dict[question.id].id = storage_id
            else:
                 logger.error("Unable to locate question with id " + str(question.id) + " in response_dict")
    
    def get_answer_storage(self, question):
        if self.in_form_object(question):
            storage = self.form_object.id
        elif question.id in self.response_dict:
            storage = self.response_dict[question.id].id
        else:
            storage = None
        
        return storage
    
    def invalidate_cards(self):
        for card_list in self.card_dict.values():
                for card in card_list:
                    card.invalidate()        
    
    def save(self):
        with transaction.atomic():
            self.form_object.pre_save(self)
            
            self.form_object.save()
            for response in self.response_dict.values():
                response.parent = self.form_object
                response.save()
            
            for card_list in self.card_dict.values():
                for card in card_list:
                    if card.is_valid:
                        card.save()
                    else:
                        card.delete()
            
            self.form_object.post_save(self)
    
    def delete(self):
        with transaction.atomic():
            for card_list in self.card_dict.values():
                for card in card_list:
                    card.delete()
            
            for response in self.response_dict.values():
                response.delete()
            
            self.form_object.delete()
    
    @staticmethod
    def find_form(form_type_name, country_id):
        form = Form.current_form(form_type_name, country_id)
        return form
            
    @staticmethod
    def get_form_class(form):
        mod = __import__(form.storage.module_name, fromlist=[form.storage.form_model_name])
        form_class = getattr(mod, form.storage.form_model_name)
        return form_class
    
    @staticmethod
    def find_object_by_number(key_value, form_type_name, country=None):
        form_object = None
        if country is None:
            forms = Form.objects.filter(form_type__name=form_type_name)
        else:
            forms = Form.objects.filter(form_type__name=form_type_name, operating_country=country)
            
        for form in forms:
            mod = __import__(form.storage.module_name, fromlist=[form.storage.form_model_name])
            form_class = getattr(mod, form.storage.form_model_name)
            key_field = form_class.key_field_name()
            try:
                form_object = eval('form_class.objects.get(' + key_field + '=key_value)')
            except ObjectDoesNotExist:
                pass
        
        return form_object
    
    @staticmethod
    def find_object_by_id(id, form):
        form_class = form.find_form_class()
        form_object = form_class.objects.get(id=id)       
        
        return form_object
            
        