from django.db import models
from django.contrib.postgres.fields import JSONField
from dataentry.models import Country

#
# Storage is used to describe the relationship between questions on a form
# and the storage of that data in models.  For example, the VIF model contains
# two instance of the Person model - the victim and the guardian.  To reflect
# this we could have data like
#   id   model_name        parent_storage    foreign_key_field_parent    foreign_key_field_child
#   10   VictimInterview   null              null                        null
#   11   Person            10                victim                      null                    
#   14   Person            10                guardian                    null
class Storage(models.Model):
    model_name = models.CharField(max_length=126)
    parent_storage = models.ForeignKey('self', null=True)
    foreign_key_field_parent = models.CharField(max_length=126, null=True)
    foreign_key_field_child = models.CharField(max_length=126, null=True)

class FormType(models.Model):
    name = models.CharField(max_length=126) # IRF, VIF, CEF, etc.


class Form(models.Model):
    form_type = models.ForeignKey(FormType)
    country = models.ForeignKey(Country, null=True)
    storage = models.ForeignKey(Storage)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    
    def to_form_dict(self, environment): 
        form_dict = {}
        form_dict['name'] = self.form_type.name
        form_dict['country_id'] = self.form_type.country.id
        
        return form_dict
            
        

class CategoryType(models.Model):
    name = models.CharField(max_length=126) # Grid, Card, etc.

class Category(models.Model):
    form = models.ForeignKey(Form)
    category_type = models.ForeignKey(CategoryType)
    name = models.CharField(max_length=126)
    order = models.PositiveIntegerField(null=True, blank=True)
    column_layout = models.CharField(max_length=126)
    
    def to_form_dict(self, environment): 
        form_dict = {}
        form_dict['id'] = self.id
        form_dict['name'] = self.name
        form_dict['type'] = 'grid'
        form_dict['order'] = self.order
        form_dict['layout'] = self.layout
        
        return form_dict

# Typically, there will be multiple instances of card data
# CardForm identifies a separate subform for the data on a card
class CardStorage(models.Model):
    category = models.ForeignKey(Category)
    storage = models.ForeignKey(Storage)

class AnswerType(models.Model):
    name = models.CharField(max_length=126) # Multiple Choice, Int, Address, Phone Num, etc.

class Question(models.Model): 
    prompt = models.CharField(max_length=126)
    description = models.CharField(max_length=126)
    answer_type = models.ForeignKey(AnswerType)
    params=JSONField()   # custom parameters for this question type
    
    
    def to_form_dict(self, environment):
        form_dict = {}
        form_dict['prompt'] = self.prompt
        form_dict['answer_type'] = self.answer_type
        for key, value in parms.items():
            form_dict[key] = value
        return form_dict

class QuestionLayout(models.Model):
    question = models.ForeignKey(Question)
    category = models.ForeignKey(Category)
    layout = models.CharField(max_length=126) # "1.4.2.1"
    span = models.PositiveIntegerField(null=True)
    
    def to_form_dict(self, environment):
        form_dict = {}
        form_dict['layout'] = self.layout
        form_dict['span'] = self.span
        form_dict.update(self.question.to_form_dict)
        
        return form_dict

    
class Answer(models.Model):
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=100000, null=True)
    code = models.CharField(max_length=125, null=True)
    params=JSONField()   # custom parameters for this answer type

class AnswerLayout(models.Model):
    answer = models.ForeignKey(Answer)
    category = models.ForeignKey(Category)
    layout = models.CharField

class PreviewLayout(models.Model):
    question = models.ForeignKey(Question)
    answer_part = models.CharField(max_length=126, null=True)
    category = models.ForeignKey(Category)
    layout = models.CharField(max_length=126)
    span = models.PositiveIntegerField(null=True)
    answer_type = models.ForeignKey(AnswerType)
    
    def to_form_dict(self, environment):
        preview_dict = {}
        preview_dict['question_id'] = self.question.id
        if self.answer_part is not None:
            preview_dict['answer_part'] = self.answer_part
        preview_dict['span'] = self.span
        preview_dict['layout'] = self.layout
        preview_dict['display_type'] = answer_type.name
        return preview_dict

class AnswerDictionary:
    @staticmethod
    def additional_parameters(answer):
        additional = {}
        for key, value in answer.params.items():
            additional[key] = value
        return additional
    
    @staticmethod
    def evaluate_query(answer, environment):
        data = []
        module_name = answer.params.get('module')
        model_name = answer.params.get('model')
        filter_list = answer.params.get('filter')
        field = answer.params.get('field')
        if module_name is not None and model_name is not None and filter_list is not None and field is not None:
            mod = __import__(module, fromlist=[model_name])
            the_model = getattr(mod, model_name, None)
            if the_model is not None:
                queryset = the_model.objects.all()
                for filter in filter_list:
                    queryset = queryset.eval(filter) 
                for obj in queryset:
                    val = getattr(obj, field, default=None)
                    if val is not None:
                        data.append(val)

        return data
    
    @staticmethod
    def string_to_form_dict(answers, environment):
        answer_dict = {}
        answer_dict.update(additional_parameters(answer[0]))
        return answer_dict
    
    @staticmethod
    def radio_button_to_form_dict(answers, environment):
        answer_dict = {}
        choices = []
        for answer in answers:
            choice_dict = {}
            choice_dict['value'] = answer.value
            choice_dict.update(additional_parameters(answer))
                
            answer_layout = AnswerLayout.objects.get(answer=answer)
            choice['layout'] = answer_layout.layout
            choice['span'] = answer_layout.span
            choices.append(choice)
        answer_dict['choices'] = choices
            
        return answer_dict
        
    @staticmethod
    def dropdown_to_form_dict(answers, environment):
        answer_dict = {}
        choices = []
        for answer in answers:
            if answer.value is None:
                choices = choices + evaluate_query(answer, environment)
            else:
                choice = {}
                choice['value'] = answer.value
                choices.append(choice)
        
        answer_dict['choices'] = choices
            
        return answer_dict
    
    @staticmethod
    def address_to_form_dict(answers, environment):
        answer_dict = {}
        for answer in answers:
            answer_layout = AnswerLayout.objects.get(answer=answer)
            element = {}
            element['layout'] = answer_layout.layout
            element['span'] = answer_layout.span
            answer_dict[answer.value] = element
        return answer_dict
    
    @staticmethod
    def person_to_form_dict(answers, environment):
        answer_dict = {}
        for answer in answers:
            answer_layout = AnswerLayout.objects.get(answer=answer)
            element = {}
            element['layout'] = answer_layout.layout
            element['span'] = answer_layout.span
            answer_dict[answer.value] = element
        return answer_dict
    
class QuestionLayoutDictionary:
    process_answers = {
        'String' : AnswerDictionary.string_to_form_dict,
        'RadioButtion' : AnswerDictionary.radio_button_to_form_dict,
        'Dropdown' : AnswerDictionary.dropdown_to_form_dict,
        'Address' : AnswerDictionary.address_to_form_dict,
        'Person' : AnswerDictionary.person_to_form_dict,
    }
    
    @staticmethod
    def to_form_dict(question_layout):
        question_dict = question_layout.to_form_dict(environment)
        
        answers = Answer.objects.filter(question = question_layout.question)
        if question_layout.question.answer_type.name in process_answers:
            answer_dict = process_answers[question_layout.question.answer_type.name](answer_layouts, environment)
            form_dict.update(answer_dict)    
        return question_dict

class CategoryDictionary:
    @staticmethod
    def to_form_dict(category, environment):
        
        category_dict = category.to_form_dist(environment)
        
        question_list = []
        questions = QuestionLayout.objects.filter(category=category)
        for question in questions:
            question_list.append(QuestionLayoutDictionary.to_form_dict(question, environment))
        category_dict['questions'] = question_list
        
        preview_list = []
        previews + PreviewLayout.objects.filter(category=category)
        for preview in previews:
            preview_list.append(preview.to_form_dict(environment))
        category_dict['preview'] = preview_list
        return category_dict
    
class FormDictionary:
    @staticmethod
    def to_form_dict (form, environment):
        form_dict = form.to_form_dict(environment)
        category_list = []
        categories = Category.objects.filter(form = form)
        for category in categories:
            category_list.append(category.to_form_dict(environment))
        
        form_dict['categories'] = category_list
        return form_dict

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
# Foreign storage is used when one or more question responses should be stored in a
# separate form.  For example, we would like to store the responses for
# questions related to a person using the Person model.
class QuestionStorage(models.Model):
    question = models.ForeignKey(Question)
    field_name = models.CharField(max_length=100)
    foreign_storage = models.ForeignKey(Storage, null=True)

 
class ExportImport(models.Model):
    description = models.CharField(max_length=126, null = True)
    implement_class_name = models.CharField(max_length=126, null=True)
    
class Export_Import_Question(models.Model):
    export_import = models.ForeignKey(ExportImport)
    question = models.ForeignKey(Question)
    position = models.PositiveIntegerField()
    field_type = models.CharField(max_length=126)
    export_name = models.CharField(max_length=126)
    arguments_json = JSONField()

class GoogleSheet(models.Model):
    export_import = models.ForeignKey(ExportImport)
    export_or_import = models.CharField(max_length=10)
    spreadsheet_name = models.CharField(max_length=126)
    sheet_name = models.CharField(max_length=126)
    key_column = models.CharField(max_length=126)
    import_status_column = models.CharField(max_length=126, null = True)
    import_issue_column = models.CharField(max_length=126, null=True)
    
    
class ExportImportCard(models.Model):
    export_import = models.ForeignKey(ExportImport, related_name='export_import_base', null=True)
    card_export_import = models.ForeignKey(ExportImport, related_name='export_import_card', null=True)
    start_position = models.PositiveIntegerField()
    prefix = models.CharField(max_length=126)
    max_instances = models.PositiveIntegerField()

# Class to store an instance of the IRF data.
# This should contain data that is common for all IRFs and is not expected to be changed
class Irf(models.Model):
    form = models.ForeignKey(Form)
    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    location = models.CharField('Location:', max_length=255)
    date_time_of_interception = models.DateTimeField('Date/Time:')
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)
    staff_name = models.CharField('Staff Name:', max_length=255)
    

# Store the responses to questions that are not stored directly in the Irf model.  Includes questions that may
# be changed in the future.  For "Open Response" and "Multi Other Response" where an non-standard answer has
# been provided, the value of answer will be null.
class IrfResponse(models.Model):
    irf = models.ForeignKey(Irf)
    question = models.ForeignKey(Question)
    value = models.CharField(max_length=100000, null=True)


    
    
