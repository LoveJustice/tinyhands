import pytz
import datetime
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import make_aware

from accounts.models import Account

from .border_station import BorderStation
from .country import Country

#
# Storage is used to describe the relationship between questions on a form
# and the storage of that data in models.  For example, the VIF model contains
# two instance of the Person model - the victim and the guardian.  To reflect
# this we could have data like
#   id   module_name                   form model_name            response_model_name parent_storage foreign_key_field_parent    foreign_key_field_child
#   10   dataentry.models.vif          Vif                        VifResponse         null           null                        null
#   11   dataentry.models.person_box   VictimInterviewPersonBox   null                10             null                        victim_interview                    
#   14   dataentry.models.location_box VictimInterviewLocationBox null                10             null                        victim_interview
class Storage(models.Model):
    module_name = models.CharField(max_length=126)
    form_model_name = models.CharField(max_length=126)
    response_model_name = models.CharField(max_length=126, null=True)
    parent_storage = models.ForeignKey('self', null=True)
    foreign_key_field_parent = models.CharField(max_length=126, null=True)
    foreign_key_field_child = models.CharField(max_length=126, null=True)

class FormType(models.Model):
    name = models.CharField(max_length=126) # IRF, VIF, CEF, etc.

class Form(models.Model):
    form_type = models.ForeignKey(FormType)
    storage = models.ForeignKey(Storage)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    form_name = models.CharField(max_length=126)
    
    stations = models.ManyToManyField(BorderStation)
    
    def find_form_class(self):
        mod = __import__(self.storage.module_name, fromlist=[self.storage.form_model_name])
        form_class = getattr(mod, self.storage.form_model_name)
        return form_class
        
    @staticmethod
    def current_form(form_type_name, station_id):
        today = make_aware(datetime.datetime.now())
        form_list = Form.objects.filter(form_type__name=form_type_name, start_date__lte=today, end_date__gte=today, stations__id=station_id)
        if len(form_list) > 0:
            return form_list[0]
        else:
            return None
    

class CategoryType(models.Model):
    name = models.CharField(max_length=126) # Grid, Card, etc.

class Category(models.Model):
    form = models.ForeignKey(Form)
    category_type = models.ForeignKey(CategoryType)
    name = models.CharField(max_length=126)
    order = models.PositiveIntegerField(null=True, blank=True)

# Typically, there will be multiple instances of card data
# CardForm identifies a separate subform for the data on a card
class CardStorage(models.Model):
    category = models.ForeignKey(Category)
    storage = models.ForeignKey(Storage)

class AnswerType(models.Model):
    name = models.CharField(max_length=126) # Multiple Choice, Int, Address, Phone Num, etc.

class Question(models.Model): 
    prompt = models.CharField(max_length=126, blank=True)
    description = models.CharField(max_length=126, null=True)
    answer_type = models.ForeignKey(AnswerType)
    params=JSONField(null=True)   # custom parameters for this question type
    export_name = models.CharField(max_length=126, null=True)
    export_params = JSONField(null=True)
    
    def export_header_Address(self, prefix):
        if self.export_name is not None and  self.export_name != '':
            prefix = prefix + export_name + ' '
 
        export_header_list = [
            prefix + 'address1', 
            prefix + 'address2']
        
        return export_header_list
        
    
    def export_header_Person(self, prefix):
        if self.export_name is not None and  self.export_name != '':
            prefix = prefix + export_name + ' '
    
        export_header_list = [
            prefix + 'name', 
            prefix + 'gender',
            prefix + 'age',
            prefix + 'address1',
            prefix + 'address2',
            prefix + 'phone',
            prefix + 'birthdate',
            prefix + 'passport',
            prefix + 'nationality',
            ]
        
        return export_header_list
    
    def export_headers(self, prefix):
        header_method_name = 'export_header_' + self.answer_type.name
        header_method = getattr(self, header_method_name, None)
        if header_method is not None:
            headers = header_method(prefix)
        else:
            if self.export_name is None:
                headers = [prefix + '']
            else:
                headers = [prefix + self.export_name]
        
        return headers
    
    def format_DateTime(self, answer, station):
        if answer is None:
            formatted_answer_list = ['']
        else:
            tz = pytz.timezone(station.time_zone)
            date_time = answer.astimezone(tz)
            formatted_answer_list = [str(date_time.replace(tzinfo=None))]
        return formatted_answer_list
    
    def format_Address(self, answer, station):
        if answer is None:
            formatted_answer_list = [
                    '',
                    ''
                ]
        else:
            formatted_answer_list = [
                    answer.address1.name,
                    answer.name
                ]
        
        return formatted_answer_list
    
    def format_Person(self, answer, station):
        if answer is None:
            formatted_answer_list = ['','','','','','','','','']
        else:
            formatted_answer_list = []
            formatted_answer_list.append(getattr(answer, 'full_name', ''))
            formatted_answer_list.append(getattr(answer, 'gender', ''))
            formatted_answer_list.append(getattr(answer, 'age',''))
            tmp = getattr(answer, 'address1', None)
            if tmp is None:
                formatted_answer_list.append('')
            else:
                formatted_answer_list.append(tmp.name)
            tmp = getattr(answer, 'address2', None)
            if tmp is None:
                formatted_answer_list.append('')
            else:
                formatted_answer_list.append(tmp.name)
            formatted_answer_list.append(getattr(answer, 'phone_contact', ''))
            tmp = getattr(answer, 'birthdate', None)
            if tmp is None:
                formatted_answer_list.append('')
            else:
                formatted_answer_list.append(str(tmp))
            formatted_answer_list.append(getattr(answer, 'passport',''))
            formatted_answer_list.append(getattr(answer, 'nationality',''))
        
        return formatted_answer_list
    
    def format_answer_map(self, answer):
        if self.export_params is not None and 'answer_map' in self.export_params and self.export_params['answer_map'] == True:
            answers = Answer.objects.filter(question=self.question, code=answer)
            if len(answers) > 0:
                formatted_answer = answers[0].value
            else:
                formatted_answer = answer
        else:
            formatted_answer = answer
        
        return [formatted_answer]
    
    def format_RadioButton(self, answer, station):
        if answer is None:
            formatted_answer = ['']
        else:
            formatted_answer = self.format_answer_map(answer)
        return formatted_answer
    
    def format_DropDown(self, answer, station):
        if answer is None:
            formatted_answer = ['']
        else:
            formatted_answer = self.format_answer_map(answer)
        return formatted_answer
    
    def format_default(self, answer, station):
        if answer is None:
            formatted_answer_list = ['']
        else:
            formatted_answer_list = [answer]
        return formatted_answer_list
    
    def export_value(self, form_data, main_data):
        if form_data is None:
            answer = None
        else:
            answer = form_data.get_answer(self)
        format_method_name = 'format_' + self.answer_type.name
        format_method = getattr(self, format_method_name, None)
        if format_method is not None:
            answer_list = format_method(answer, main_data.form_object.station)
        else:
            answer_list = self.format_default(answer, main_data.form_object.station)
        
        if self.export_params is not None and 'map' in self.export_params and len(answer_list) == 1:
            the_map = self.export_params['map']
            print ('mapping', answer_list, the_map)
            if answer_list[0] in the_map:
                answer_list = [the_map[answer_list[0]]]
            elif 'default' in the_map:
                answer_list = [the_map['default']]
                
        return answer_list

class QuestionLayout(models.Model):
    question = models.ForeignKey(Question)
    category = models.ForeignKey(Category)
    weight = models.IntegerField(default=0)
    
class Answer(models.Model):
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=100000, null=True)
    code = models.CharField(max_length=125, null=True)
    params=JSONField(null=True)   # custom parameters for this answer type


# Identifies validation for IRF or VIF form
#  GENERIC
#    - not_blank_or_null verifies that the answers to the questions are not blank or null
#    - at_least_one_true verifies that at least one of the answers to the questions is true
#  CUSTOM
#    - at_least_one_interceptee verifies that there is at least one interceptee on the IRF
#    - name_came_up_before verifies the answer for the name came up before question on the IRF
#    - trafficker_custody verifies answer for the trafficker taken into custody question on the IRF
class FormValidationType(models.Model):
    name = models.CharField(max_length=126)

# basic_error  - prevents form from being saved (cannot save form with pending status)
# submit_error - prevents form from being submitted (cannot save form with active status)
# warning      - can be overridden to allow the form to be submitted
class FormValidationLevel(models.Model):
    name = models.CharField(max_length=126)

# form - the form on which the question(s) should be validated
# trigger - question whose answer determines if the validation should be performed
#    If trigger question is not null and the answer to the trigger question is true, the validation should be performed
#    If trigger question is null, the validation should always be performed
# validation_type - Is the type of validation to be performed on the questions
# error_warning_message - message returned to client when validation fails
class FormValidation(models.Model):
    form = models.ForeignKey(Form)
    level = models.ForeignKey(FormValidationLevel)
    trigger = models.ForeignKey(Question, null=True)
    trigger_value = models.CharField(max_length=126, null=True)
    validation_type = models.ForeignKey(FormValidationType)
    error_warning_message = models.CharField(max_length=126)

# Set of questions to be validated for the FormValidation
class FormValidationQuestion(models.Model):
    validation = models.ForeignKey(FormValidation)
    question = models.ForeignKey(Question)

class Condition(models.Model):
    condition = JSONField() 
    # {"type":"red", {12: "true", 14: "false"}, points: 10}
    # Type determines red flag,warning,home situation, etc.
    # Second dictionary associates question with answer (dereferenced to use value in this example)
    # Points would make sense for conditions that may cummulate in their severity

#
# QuestionStorage is used to specify that the question response will be
# stored in a field of the forms model as opposed to being stored as a
# generic response.
# For example, an entry could specify that the response to the 'IRF Number'
# question would be stored in the field name 'irf_number'
class QuestionStorage(models.Model):
    question = models.ForeignKey(Question)
    field_name = models.CharField(max_length=100)

 #
 #  Work still needed on the export/import classes
 #
class ExportImport(models.Model):
    description = models.CharField(max_length=126, null = True)
    implement_module = models.CharField(max_length=126, null=True)
    implement_class_name = models.CharField(max_length=126, null=True)
    form = models.ForeignKey(Form)

class ExportImportQuestion(models.Model):
    export_import = models.ForeignKey(ExportImport)
    question = models.ForeignKey(Question)
    export_name = models.CharField(max_length=126)
    arguments_json = JSONField(null=True)
    
    def format_DateTime(self, answer, station):
        tz = pytz.timezone(station.time_zone)
        date_time = answer.astimezone(tz)
        return str(date_time.replace(tzinfo=None))
    
    def format_parts(self, answer):
        if self.arguments_json is not None and 'part' in self.arguments_json:
            part_list = self.arguments_json['part'].split('.')
            formatted_answer = answer
            for part in part_list:
                if formatted_answer is None:
                    break
                formatted_answer = getattr(formatted_answer, part, None)
        else:
            # log error
            formatted_answer = None
        
        return formatted_answer
    
    def format_Address(self, answer, station):
        return self.format_parts(answer)
    
    def format_Person(self, answer, station):
        return self.format_parts(answer)
    
    def format_answer_map(self, answer):
        if self.arguments_json is not None and 'answer_map' in self.arguments_json and self.arguments_json['answer_map'] == True:
            answers = Answer.objects.filter(question=self.question, code=answer)
            if len(answers) > 0:
                formatted_answer = answers[0].value
            else:
                formatted_answer = answer
        else:
            formatted_answer = answer
        
        return formatted_answer
    
    def format_RadioButton(self, answer, station):
        return [self.format_answer_map(answer)]
    
    def format_DropDown(self, answer, station):
        return [self.format_answer_map(answer)]
    
    def export_value(self, form_data, main_data):
        answer = form_data.get_answer(self.question)
        if answer is not None:
            format_method_name = 'format_' + self.question.answer_type.name
            format_method = getattr(self, format_method_name, None)
            if format_method is not None:
                answer = format_method(answer, main_data.form_object.station)
        
        if self.arguments_json is not None and 'map' in self.arguments_json:
            the_map = self.arguments_json['map']
            print ('mapping', answer, the_map)
            if answer in the_map:
                answer = the_map[answer]
            elif 'default' in the_map:
                answer = the_map['default']
                
        if answer is None:
            answer = ''
                
        return answer
        

class GoogleSheet(models.Model):
    export_import = models.ForeignKey(ExportImport)
    export_or_import = models.CharField(max_length=10)
    spreadsheet_name = models.CharField(max_length=126)
    sheet_name = models.CharField(max_length=126)
    key_field_name = models.CharField(max_length=126)
    import_status_column = models.CharField(max_length=126, null = True)
    import_issue_column = models.CharField(max_length=126, null=True)

class ExportImportCard(models.Model):
    export_import = models.ForeignKey(ExportImport, related_name='export_import_base')
    category = models.ForeignKey(Category, related_name='export_import_card')
    prefix = models.CharField(max_length=126)
    max_instances = models.PositiveIntegerField()
    


# data fields to be exported for which there is no question
class ExportImportField(models.Model):
    export_import = models.ForeignKey(ExportImport)
    card = models.ForeignKey(ExportImportCard, null=True)
    field_name = models.CharField(max_length=126)
    answer_type = models.ForeignKey(AnswerType, related_name='field_answer_type')
    export_name = models.CharField(max_length=126)
    arguments_json = JSONField(null=True)
    
    def format_DateTime(self, answer, station):
        print('in field format date/time', station)
        tz = pytz.timezone(station.time_zone)
        date_time = answer.astimezone(tz)
        return str(date_time.replace(tzinfo=None))
    
    def format_parts(self, answer):
        if self.arguments_json is not None and 'part' in self.arguments_json:
            part_list = self.arguments_json['part'].split('.')
            formatted_answer = answer
            for part in part_list:
                if formatted_answer is None:
                    break
                formatted_answer = getattr(formatted_answer, part, None)
        else:
            # log error
            formatted_answer = None
        
        return formatted_answer
    
    def format_Address(self, answer, station):
        return self.format_parts(answer)
    
    def format_Person(self, answer, station):
        return self.format_parts(answer)
    
    def export_value(self, form_obj, main_data):
        answer = getattr(form_obj, self.field_name)
        if answer is not None:
            format_method_name = 'format_' + self.answer_type.name
            print ('field export_value', format_method_name)
            format_method = getattr(self, format_method_name, None)
            if format_method is not None:
                answer = format_method(answer, main_data.form_object.station)
        
        if self.arguments_json is not None and 'map' in self.arguments_json:
            the_map = self.arguments_json['map']
            print ('mapping', answer, the_map)
            if answer in the_map:
                answer = the_map[answer]
            elif 'default' in the_map:
                answer = the_map['default']
                
        return answer

class BaseForm(models.Model):
    status = models.CharField('Status', max_length=20, default='pending')
    station = models.ForeignKey(BorderStation)
    date_time_entered_into_system = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)
    form_entered_by = models.ForeignKey(Account, related_name='%(class)s_entered_by', null=True)
    
    class Meta:
        abstract = True
    
    # Overridden in subclass
    def get_key(self):
        return None
    
    # Overridden in subclass as needed
    def pre_save(self, form_data):
        pass
    
    def post_save(self, form_data):
        pass
        
class BaseResponse(models.Model):
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=100000, null=True)
    
    class Meta:
        abstract = True
        
class BaseCard(models.Model):
    class Meta:
        abstract = True
    
    def setParent(self, the_parent):
        raise NotImplementedError("set parent not defined in card model")