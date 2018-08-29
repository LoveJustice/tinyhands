import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from .models.form import Category, FormValidation, FormValidationQuestion, QuestionLayout, QuestionStorage

logger = logging.getLogger(__name__);

class ValidateForm:
    # Format and add a message to the error or warning lists
    def add_error_or_warning(self, category_name, category_index, validation):
        if category_index is not None:
            msg = category_name + ' ' + str(category_index) + ':' + validation.error_warning_message
        else:
            msg = category_name + ':' + validation.error_warning_message 
            
        if validation.level.name == 'warning':
            self.warnings.append(msg)
        else:
            self.errors.append(msg)
        
        self.response_code = status.HTTP_400_BAD_REQUEST

    # Retrieve the answer value from the form or from the response objects
    def get_answer(self, question, form, responses):
        try:
            # answer is stored in form model
            question_storage = QuestionStorage.objects.get(question=question)
            answer = getattr(form, question_storage.field_name, None)
        except ObjectDoesNotExist:
            answer = None
            for response in responses:
                if response.question == question:
                    answer = response.value
        
        return answer

    def not_blank_or_null(self, form_data, validation, validation_questions, category_index, general):
        for validation_question in validation_questions:
            question = validation_question.question
            answer = form_data.get_answer(question)
            if answer is None or isinstance(answer, str) and answer.strip() == '':
                if general:
                    category_name = ''
                else:
                    category_name = self.question_map[question.id]
                self.add_error_or_warning(category_name, category_index, validation)
            
    
    def at_least_one_true(self, form_data, validation, validation_questions, category_index, general):   
        for validation_question in validation_questions:
            question = validation_question.question
            answer = form_data.get_answer(question)
            if answer is not None and (isinstance(answer, bool) and answer == True or isinstance(answer, str) and answer.upper() == 'TRUE'):
                # found at least one true response
                return
        
        if general:
            category_name = ''
        else:
            category_name = self.question_map[question.id]
        self.add_error_or_warning(category_name, category_index, validation)
    
    def at_least_one_card (self, form_data, validation, questions, category_index, general):
        for cat_list in form_data.card_dict.values():
            if len(cat_list) > 0:
                return
            
        self.add_error_or_warning('CARD', None, validation)
    
    def custom_trafficker_custody(self, form_data, validation, questions, category_index, general):
        if len(questions) < 1:
            logger.error("custom_trafficker_custody validation requires at least one question")
            self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return
        
        answer = form_data.get_answer(questions[0].question)
        if answer is not None and answer.strip() != '':
            traffickers = answer.split(',')
            for trafficker in traffickers:
                if not trafficker.isdigit():
                    self.add_error_or_warning(self.question_map[questions[0].question.id], category_index, validation)
                    break
                elif int(trafficker) < 1 or int(trafficker) > 12:
                    self.add_error_or_warning(self.question_map[questions[0].question.id], category_index, validation)
                    break
    
    def form_id_station_code(self, form_data, validation, questions, category_index, general):
        if len(questions) < 1:
            logger.error("form_id_station_code validation requires at least one question")
            return
        
        question = questions[0].question
        if general:
            category_name = ''
        else:
            category_name = self.question_map[question.id]
        answer = form_data.get_answer(question)
        station_code = form_data.form_object.station.station_code
        if not answer.startswith(station_code):
            self.add_error_or_warning(category_name, category_index, validation)            

    
    def __init__(self, form, form_data, ignore_warnings):
        self.validations = {
            'not_blank_or_null': self.not_blank_or_null,
            'at_least_one_true': self.at_least_one_true,
            'at_least_one_card': self.at_least_one_card,
            'trafficker_custody': self.custom_trafficker_custody,
            'form_id_station_code': self.form_id_station_code
        }
        
        self.validations_to_perform = {
            'basic_error': True,
        }
        
        self.main_form = 'main_form'
        self.form_data = form_data
        self.form = form
        self.data = form_data.form
        self.responses = form_data.response_dict
        self.cards = form_data.card_dict
        self.response_code = status.HTTP_200_OK
        
        if self.form_data.form_object.status == 'approved':   
            self.validations_to_perform['submit_error'] = True
            if not ignore_warnings:
                self.validations_to_perform['warning'] = True

        self.errors = []
        self.warnings = []
        
        # Map a question id to a category name
        self.question_map = {}
        
        # Map a question id to validation set
        #  There is one entry for the main form
        #  There is one entry for each card category
        #     Each entry has a list of validations to be performed
        question_to_validation_set = {}
        
        categories = Category.objects.filter(form = form)
        for category in categories:
            layouts = QuestionLayout.objects.filter(category=category)
            for layout in layouts:
                self.question_map[layout.question.id] = category.name
                if category.category_type.name == 'card':
                    question_to_validation_set[layout.question.id] = category.id
                else:
                    question_to_validation_set[layout.question.id] = self.main_form
        
        self.validation_set = {}
        validations = FormValidation.objects.filter(form=self.form)
        for validation in validations:
            if validation.trigger is not None:
                set_key = question_to_validation_set[validation.trigger.id]
                if set_key not in self.validation_set:
                    self.validation_set[set_key] = [ validation ]
                else:
                    self.validation_set[set_key].append(validation)
            else:                   
                validation_questions = FormValidationQuestion.objects.filter(validation=validation)
                if len(validation_questions) > 0:
                    for validation_question in validation_questions:
                        set_key = question_to_validation_set[validation_question.question.id]
                        if set_key not in self.validation_set:
                            self.validation_set[set_key] = [ validation ]
                        else:
                            self.validation_set[set_key].append(validation)
                        
                        break
                else:
                    self.validation_set[self.main_form].append(validation)
                    
   
    
    def perform_validation(self, validation, form_data, category_index=None):
        if validation.level.name in self.validations_to_perform:
            if validation.trigger is not None:
                trigger_value = form_data.get_answer(validation.trigger)
                if validation.trigger_value is not None:
                    if trigger_value == validation.trigger_value:
                        should_validate = True
                    else:
                        should_validate = False
                else:
                    if isinstance(trigger_value, bool) and trigger_value:
                        should_validate = True
                    elif isinstance(trigger_value, str) and trigger_value.upper() == 'TRUE':
                        should_validate = True
                    else:
                        should_validate = False
            else:
                should_validate = True
        
            if should_validate:
                questions = FormValidationQuestion.objects.filter(validation=validation)
                general = False
                the_category = None
                for question in questions:
                    if the_category is None:
                        the_category = self.question_map[question.question.id]
                    elif the_category != self.question_map[question.question.id]:
                        general = True
                        break                           
                self.validations[validation.validation_type.name](form_data, validation, questions, category_index, general)
         
    def validate(self):
        if self.main_form in self.validation_set:
            for validation in self.validation_set[self.main_form]:
                if validation.validation_type.name in self.validations:
                    self.perform_validation(validation, self.form_data)
                else:
                    logger.error("validation #" + validation.id + " specifies an unimplemented validation:" + validation.validation_type.name)
                    self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        for category_id, card_list in self.form_data.card_dict.items():
            category_count = 0
            for card in card_list:
                category_count += 1
                
                if category_id in self.validation_set:
                    for validation in self.validation_set[category_id]:
                        if validation.validation_type.name in self.validations:
                            self.perform_validation(validation, card, category_index=card_index)
                        else:
                            logger.error("validation #" + str(validation.id) + " specifies an unimplemented validation:" + validation.validation_type.name)
                            self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        
        
            
                