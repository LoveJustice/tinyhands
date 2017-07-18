from django.db import models
from django.contrib.postgres.fields import JSONField
from dataentry.models import Country

class Form(models.Model):
    form_type = models.ForeignKey(FormType)
    country = models.ForeignKey(Country, null=True)
    storage = models.ForeignKey(Storage)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)

class FormType(models.Model):
    name = models.CharField(max_length=100) # IRF, VIF, CEF, etc.

class Category(models.Model):
    form = models.ForeignKey(Form)
    category_type = models.ForeignKey(CategoryType)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(null=True, blank=True)

class CategoryType(models.Model):
    name = models.CharField(max_length=100) # Grid, Card, etc.

# Typically, there will be multiple instances of card data
# CardForm identifies a separate subform for the data on a card
class CardForm(models.Model):
    category = models.ForeignKey(Category)
    subform = models.ForeignKey(Form)

class Question(models.Model):
    answer_type = models.ForeignKey(AnswerType)
    description = models.CharField(max_length=100)

class QuestionLayout(models.Model):
    question = models.ForeignKey(Question)
    category = models.ForeignKey(Category)
    layout = models.CharField(max_length=100) # "1.4.2.1"
    
class QuestionTranslation(models.Model):
    question = models.ForeignKey(Question)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100)

class AnswerType(models.Model):
    name = models.CharField(max_length=100) # Multiple Choice, Int, Address, Phone Num, etc.

class Answer(models.Model):
    question = models.ForeignKey(Question)
    answer_type = models.ForeignKey(AnswerType)
    value = models.CharField(max_length=100)

class AnswerLayout(models.Model):
    answer = models.ForeignKey(Answer)
    category = models.ForeignKey(Category)
    layout = models.CharField(max_length=100)

class Prompt(models.Model):
    layout = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

class Condition(models.Model):
    condition = JSONField() 
    # {"type":"red", {12: "true", 14: "false"}, points: 10}
    # Type determines red flag,warning,home situation, etc.
    # Second dictionary associates question with answer (dereferenced to use value in this example)
    # Points would make sense for conditions that may cummulate in their severity

# -- Translation Models --
class Language(models.Model):
    name = models.CharField(max_length=100)

class CategoryTranslation(models.Model):
    category = models.ForeignKey(Category)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100)

class AnswerTranslation(models.Model):
    answer = models.ForeignKey(Answer)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100) # Longer?

class PromptTranslation(models.Model):
    prompt = models.ForeignKey(Prompt)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100) # Longer?

class ConditionTranslation(models.Model):
    condition = models.ForeignKey(Condition)
    language = models.ForeignKey(Language)
    text = models.CharField(max_length=100) # Longer?
    # This would allow for a message to be displayed if condition is satisfied
    
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

#
# Storage is used to describe the relationship between questions on a form
# and the storage of that data in models.  For example, the VIF model contains
# two instance of the Person model - the victim and the guardian.  To reflect
# this we could have data like
#   id   model_name        parent_storage    foreign_key_field_name
#   10   VictimInterview   null              null
#   11   Person            10                victim
#   12   Address1          11                address1
#   13   Address2          11                address2
#   14   Person            10                guardian
#   15   Address1          14                address1
#   16   Address2          14                address2
class Storage(model.Model):
    model_name = models.CharField(max_length=100)
    parent_storage = models.ForeignKey(Storage, null=True)
    foreign_key_field_name = models.ForeignKey(Question, null=True)


 
class ExportImport(models.Model):
    description = models.CharField(max_length=100, null = True)
    implement_class_name = models.CharField(max_length=100, null=True)
    
class Export_Import_Question(models.Model):
    export_import = models.ForeignKey(ExportImport)
    question = models.ForeignKey(Question)
    position = models.PositiveIntegerField()
    field_type = models.CharField(max_length=100)
    export_name = models.CharField(max_length=100)
    arguments_json = JSONField()

class GoogleSheet(models.Model):
    export_import = models.ForeignKey(ExportImport)
    export_or_import = models.CharField(max_length=10)
    spreadsheet_name = models.CharField(max_length=100)
    sheet_name = models.CharField(max_length=100)
    key_column = models.CharField(max_length=100)
    import_status_column = models.CharField(max_length=100, null = True)
    import_issue_column = models.CharField(max_length=100, null=True)
    
    
class ExportImportCard(models.Model):
    export_import = models.ForeignKey(ExportImport, null=True)
    card_export_import = models.ForeignKey(ExportImport, null=True)
    start_position = models.PositiveIntegerField()
    prefix = models.CharField(max_length=100)
    max_instances = models.PositiveIntegerField()

# Class to store an instance of the IRF data.
# This should contain data that is common for all IRFs and is not expected to be changed
class Irf(Models.Model):
    form = models.ForeignKey(Form)
    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    date_time_of_interception = models.DateTimeField('Date/Time:')

# Store the responses to questions that are not stored directly in the Irf model.  Includes questions that may
# be changed in the future.  For "Open Response" and "Multi Other Response" where an non-standard answer has
# been provided, the value of answer will be null.
class IrfResponse(Models.Model):
    irf = models.ForeignKey(Irf)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer, null = True)

# IrfResponseTranslation contains the text response value from the "Open Response" or
# Multi Other Response" where an non-standard answer has been provided.
class IrfResponseTranslation(Models.Model):
    irf_response = models.ForeignKey(IrfResponse)
    language = models.ForeignKey(Language)
    answer_text = models.CharField(max_length=100)
    

    
    
