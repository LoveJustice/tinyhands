from django.db import transaction
from .models.form import CardStorage, Category, Form, FormType, QuestionLayout, QuestionStorage, Storage

class CardData:
    def load_responses(self):
        if self.response_model is not None:
            responses = self.response_model.objects.filter(parent = self.form_object)
            self.response_dict = {}
            for response in responses:
                self.response_dict[response.question.id] = response
        else:
            self.response_dict = {}
            
    def __init__(self, card, card_class, card_response_class, response_dict = None, form_data=None):
        self.form_data = form_data
        self.form_object = card
        self.form_model = card_class
        self.response_model = card_response_class
        
        if response_dict is None:
            self.load_responses()
        else:
            self.response_dict = response_dict
    
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
    
    def get_answer_storage(self, question):
        if self.in_form_object(question):
            storage = self.form_object.id
        elif question.id in self.response_dict:
            storage = self.response_dict[question.id].id
        else:
            storage = None
        
        return storage
    
    def save_object(self):
        self.form_object.set_parent(self.form_data.form_object)
        self.form_object.save()
        for response in self.response_dict.values():
            response.parent = self.form_object
            response.save()
        

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
        card_storage = CardStorage.objects.get(category=category)
        storage = card_storage.storage
        mod = __import__(storage.module_name, fromlist=[storage.form_model_name, storage.response_model_name])
        card_class = getattr(mod, storage.form_model_name)
        if storage.response_model_name is not None:
            card_response_class = getattr(mod, storage.response_model_name)
        else:
            card_response_class = None
        
        cards = eval('card_class.objects.filter(' + storage.foreign_key_field_parent + '__id=object.id)')
        for card in cards:
            card_list.append(CardData(card, card_class, card_response_class, form_data=self))
        
        return card_list
            
    def init_from_db(self, object, form_type_name):
        self.form_object = object
        form_type = FormType.objects.get(name=form_type_name)
        self.form = Form.current_form(form_type, object.station.operating_country)
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
            
        self.load_responses()
        
        categories = Category.objects.filter(form = self.form, category_type__name = 'card')
        self.card_dict = {}
        for category in categories:
            card_list = self.load_cards(category, object)
            self.card_dict[category.id] = card_list       
    
    def init_from_mem(self, object, response_dict, card_dict, response_model):
        self.form_object = object
        self.form_model = object.__class__
        self.response_model = response_model
        self.response_dict = response_dict
        self.card_dict = card_dict
        for card_list in card_dict.values():
            for card in card_list:
                card.form_data = self
    
    def load_question_storage(self, form):
        self.question_storage = {}
        question_ids = list(QuestionLayout.objects.filter(category__form = form).values_list('question_id', flat=True))
        question_storage_list = QuestionStorage.objects.filter(question__id__in=question_ids)
        for question_storage in question_storage_list:
            self.question_storage[question_storage.question.id] = question_storage
            
    
    def __init__(self, object, form_type_name = None, response_dict=None, card_dict=None, response_model=None, form=None):
        if form is not None:
            self.form = form
        if form_type_name is not None:
            self.init_from_db(object, form_type_name)
        elif response_dict is not None:
            self.init_from_mem(object, response_dict, card_dict, response_model)
        
        self.load_question_storage(self.form)
        self.ignore_warnings = False
    
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
    
    def get_answer_storage(self, question):
        if self.in_form_object(question):
            storage = self.form_object.id
        elif question.id in self.response_dict:
            storage = self.response_dict[question.id].id
        else:
            storage = None
        
        return storage
    
    def save_object(self):
        with transaction.atomic():
            self.form_object.save()
            for response in self.response_dict.values():
                response.parent = self.form_object
                response.save()
            
            for card_list in self.card_dict.values():
                for card in card_list:
                    card.save_object()
        