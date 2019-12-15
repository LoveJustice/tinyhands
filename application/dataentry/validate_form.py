import logging
import pytz
import re

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from rest_framework import status
from datetime import date, datetime

from .models.form import FormCategory, FormValidation, FormValidationLevel, FormValidationQuestion, Question, QuestionLayout, QuestionStorage

logger = logging.getLogger(__name__);

class ValidateForm:
    # Format and add a message to the error or warning lists
    def add_error_or_warning(self, category_name, category_index, validation, data_string=''):
        if category_index is not None:
            msg = category_name + ' ' + str(category_index) + ':' + validation.error_warning_message + ' ' + data_string
        else:
            msg = category_name + ':' + validation.error_warning_message + ' ' + data_string
            
        if validation.level.name == 'warning':
            if msg not in self.warnings:
                self.warnings.append(msg)
        else:
            if msg not in self.errors:
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
    
    def get_answer_part(self, full_answer, validation, the_part):
        answer = full_answer
        if full_answer is not None and validation.params is not None and the_part in validation.params:
            tmp = validation.params[the_part]
            if tmp is not None:
                part_names = tmp.split('.')
                for part_name in part_names:
                    answer = getattr(answer, part_name, None)
                    if answer is None:
                        break
        
        return answer
        

    def not_blank_or_null(self, form_data, validation, validation_questions, category_index, general):
        for validation_question in validation_questions:
            question = validation_question.question
            full_answer = form_data.get_answer(question)
            answer = self.get_answer_part(full_answer, validation, 'part')
                
            if answer is None or isinstance(answer, str) and answer.strip() == '':
                if general:
                    category_name = ''
                else:
                    category_name = self.question_map[question.id]
                self.add_error_or_warning(category_name, category_index, validation)
            
    
    def at_least_one_true(self, form_data, validation, validation_questions, category_index, general):
        for validation_question in validation_questions:
            question = validation_question.question
            full_answer = form_data.get_answer(question)
            answer = self.get_answer_part(full_answer, validation, 'part')
            if answer is not None and (isinstance(answer, bool) and answer == True or isinstance(answer, str) and answer.strip() != ''):
                # found at least one true response
                return
        
        if general:
            category_name = ''
        else:
            category_name = self.question_map[question.id]
        self.add_error_or_warning(category_name, category_index, validation)
    
    def at_least_one_card (self, form_data, validation, questions, category_index, general):
        if getattr(form_data, 'card_dict', None) is None or validation.params is None or 'category_id' not in validation.params:
            tmp_validation = FormValidation()
            tmp_validation.level = validation.level
            tmp_validation.error_warning_message = 'Incorrect configuration for validation:' + validation.error_warning_message
            self.add_error_or_warning('CARD', None, tmp_validation)
        else:
            category_id = validation.params['category_id']
            if category_id in form_data.card_dict:
                if len(form_data.card_dict[category_id]):
                    return
            
        self.add_error_or_warning('CARD', None, validation)
    
    def match_filter (self, card, filter):
        if 'question_id' not in filter or 'value' not in filter or 'operation' not in filter:
            return -1
        
        question = Question.objects.get(id=filter['question_id'])
        answer = card.get_answer(question)
        rv = 0
        if filter['operation'] == '=' and answer == filter['value']:
            rv = 1
        elif filter['operation'] == '!=' and answer != filter['value']:
            rv = 1
        
        return rv     
    
    def card_count (self, form_data, validation, questions, category_index, general):
        if validation.params is not None and 'category_name' in validation.params:
            category_name = validation.params['category_name']
        else:
            category_name = ''
        if (getattr(form_data, 'card_dict', None) is None or validation.params is None or 'category_id' not in validation.params or
                ('min_count' not in validation.params and 'max_count' not in validation.params)):
            tmp_validation = FormValidation()
            tmp_validation.level = validation.level
            tmp_validation.error_warning_message = 'Incorrect configuration for validation:' + validation.error_warning_message
            self.add_error_or_warning(category_name, None, tmp_validation)
        else:
            card_count = 0
            category_id = validation.params['category_id']
            if category_id in form_data.card_dict:
                for card in form_data.card_dict[category_id]:
                    if 'filter' in validation.params:
                        match_result = self.match_filter(card, validation.params['filter'])
                        if match_result >= 0:
                            card_count += match_result
                        else:
                            tmp_validation = FormValidation()
                            tmp_validation.level = validation.level
                            tmp_validation.error_warning_message = 'Incorrect filter for validation:' + validation.error_warning_message
                            self.add_error_or_warning(category_name, None, tmp_validation)
                    else:
                        card_count += 1
            
            if 'min_count' in validation.params:
                if card_count >= validation.params['min_count']:
                    return
            else:
                if card_count <= validation.params['max_count']:
                    return
            
        self.add_error_or_warning(category_name, None, validation)
    
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
            self.add_error_or_warning(category_name, category_index, validation, '"' + station_code + '"')
    
    def regex_match(self, form_data, validation, questions, category_index, general):
        if validation.params is None or 'regex' not in validation.params:
            return
        
        regex = validation.params['regex']
        
        for validation_question in questions:
            question = validation_question.question
            answer = form_data.get_answer(question)
            result = re.match(regex, answer)
            if result is None:
                 self.add_error_or_warning(self.question_map[question.id], category_index, validation)
        
    def prevent_future_date(self, form_data, validation, validation_questions, category_index, general):
        if getattr(form_data, 'form_data', None) is not None:
            tz = pytz.timezone(form_data.form_data.form_object.station.time_zone)
        else:
            tz = pytz.timezone(form_data.form_object.station.time_zone)
        now = datetime.now(tz)
        for validation_question in validation_questions:
            question = validation_question.question
            full_answer = form_data.get_answer(question)
            answer = self.get_answer_part(full_answer, validation, 'part')
            if answer is not None and answer != '':
                if isinstance(answer, date):
                    test_datetime = datetime(answer.year, answer.month, answer.day)
                elif isinstance(answer, datetime):
                    test_datetime = datetime(answer.year, answer.month, answer.day, answer.hour, answer.minute, answer.second)
                else:
                    continue
            
                test_datetime = test_datetime.astimezone(tz)
                if test_datetime > now:
                    category_name = self.question_map[question.id] + ':' + question.prompt
                    self.add_error_or_warning(category_name, category_index, validation)
    
    def check_not_null (self, category_id, form_data, category_index=None):
        validation = FormValidation()
        validation.level = FormValidationLevel.objects.get(name='basic_error')
        form_class = type(form_data.form_object)
        
        if category_id == self.main_form:
            question_layouts = QuestionLayout.objects.filter(category__in=self.main_categories)
        else:
            question_layouts = QuestionLayout.objects.filter(category__id=category_id)
            
        for question_layout in question_layouts:
            question = question_layout.question
            question_storage = QuestionStorage.objects.get(question=question)
            answer = form_data.get_answer(question)
            try:
                if not form_class._meta.get_field(question_storage.field_name).null and answer is None:
                    validation.error_warning_message = question.prompt + ' must be entered'
                    self.add_error_or_warning(self.question_map[question.id], category_index, validation)               
            except FieldDoesNotExist:
                pass

    def __init__(self, form, form_data, ignore_warnings):
        self.validations = {
            'not_blank_or_null': self.not_blank_or_null,
            'at_least_one_true': self.at_least_one_true,
            'at_least_one_card': self.at_least_one_card,
            'trafficker_custody': self.custom_trafficker_custody,
            'form_id_station_code': self.form_id_station_code,
            'prevent_future_date': self.prevent_future_date,
            'regular_expression': self.regex_match,
            'card_count': self.card_count,
        }
        
        self.validations_to_perform = {
            'basic_error': True,
        }
        
        self.main_form = 'main_form'
        self.invalid = 'invalid'
        self.form_data = form_data
        self.form = form
        self.data = form_data.form
        self.responses = form_data.response_dict
        self.cards = form_data.card_dict
        self.response_code = status.HTTP_200_OK
        
        if self.form_data.form_object.status != 'in-progress':   
            self.validations_to_perform['submit_error'] = True
            if not ignore_warnings:
                self.validations_to_perform['warning'] = True

        self.errors = []
        self.warnings = []
        self.main_categories = []
        
        # Map a question id to a category name
        self.question_map = {}
        
        # Map a question id to validation set
        #  There is one entry for the main form
        #  There is one entry for each card category
        #     Each entry has a list of validations to be performed
        question_to_validation_set = {}
        
        form_categories = FormCategory.objects.filter(form=form)
        for form_category in form_categories:
            category = form_category.category
            if category.category_type.name != 'card':
                self.main_categories.append(category)
            layouts = QuestionLayout.objects.filter(category=category)
            for layout in layouts:
                self.question_map[layout.question.id] = form_category.name
                if category.category_type.name == 'card':
                    question_to_validation_set[layout.question.id] = category.id
                else:
                    question_to_validation_set[layout.question.id] = self.main_form
                    
        self.question_to_validation_set = question_to_validation_set
        
        self.validation_set = {}
        validations = FormValidation.objects.filter(form=self.form)
        for validation in validations:
            set_key = None
            if validation.trigger is not None:
                set_key = question_to_validation_set[validation.trigger.id]
            
            validation_questions = FormValidationQuestion.objects.filter(validation=validation)
            if len(validation_questions) > 0:
                for validation_question in validation_questions:
                    tmp_key = question_to_validation_set[validation_question.question.id]
                    if set_key is None:
                        set_key = tmp_key
                    elif set_key != tmp_key:
                        self.errors.append('Validation mixes main form and card questions. Validation id=' + str(validation.id) + 
                                           ' with message=' + validation.error_warning_message)
                        set_key = self.invalid
                        break
                
            if set_key is None:
                set_key = self.main_form
            
            if set_key in self.validation_set:
                self.validation_set[set_key].append(validation)
            else:
                self.validation_set[set_key] = [validation]
                    
   
    
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
        self.check_not_null (self.main_form, self.form_data)
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
                
                self.check_not_null (category_id, card, category_index=category_count)
                
                if category_id in self.validation_set:
                    for validation in self.validation_set[category_id]:
                        if validation.validation_type.name in self.validations:
                            self.perform_validation(validation, card, category_index=category_count)
                        else:
                            logger.error("validation #" + str(validation.id) + " specifies an unimplemented validation:" + validation.validation_type.name)
                            self.response_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
        
        
            
                