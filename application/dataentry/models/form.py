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

class CategoryType(models.Model):
    name = models.CharField(max_length=126) # Grid, Card, etc.

class Category(models.Model):
    form = models.ForeignKey(Form)
    category_type = models.ForeignKey(CategoryType)
    name = models.CharField(max_length=126)
    order = models.PositiveIntegerField(null=True, blank=True)
    column_layout = models.CharField(max_length=126)

# Typically, there will be multiple instances of card data
# CardForm identifies a separate subform for the data on a card
class CardStorage(models.Model):
    category = models.ForeignKey(Category)
    storage = models.ForeignKey(Storage)

class Question(models.Model): 
    prompt = models.CharField(max_length=126)
    descriptionCate = models.CharField(max_length=126)

class QuestionLayout(models.Model):
    question = models.ForeignKey(Question)
    category = models.ForeignKey(Category)
    layout = models.CharField(max_length=126) # "1.4.2.1"
    span = models.PositiveIntegerField(null=True)

class QuestionStorage(Storage):
    question = models.ForeignKey(Question)
    storage = models.ForeignKey(Storage)
    field_name = models.CharField(max_length=126)

class AnswerType(models.Model):
    name = models.CharField(max_length=126) # Multiple Choice, Int, Address, Phone Num, etc.
    
class Answer(models.Model):
    question = models.ForeignKey(Question)
    answer_type = models.ForeignKey(AnswerType)
    value = models.CharField(max_length=100000, null=True)
    code = models.CharField(max_length=125, null=True)
    params=JSONField()   # custom parameters for this answer type

class AnswerLayout(models.Model):
    answer = models.ForeignKey(Answer)
    category = models.ForeignKey(Category)
    layout = models.CharField

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


    
    
