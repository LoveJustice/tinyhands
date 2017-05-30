from django.db import models
from django.contrib.postgres.fields import JSONField
from dataentry.models import Country

class Form(models.Model):
    form_type = models.ForeignKey(FormType, null=True)
    country = models.ForeignKey(Country, null=True)
    export_sheet = models.CharField(max_length=100)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)

class FormType(models.Model):
    name = models.CharField(max_length=100) # IRF, VIF, CEF, etc.

class Category(models.Model):
    form = models.ForeignKey(Form, null=True)
    category_type = models.ForeignKey(CategoryType, null=True)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(null=True, blank=True)

class CategoryType(models.Model):
    name = models.CharField(max_length=100) # Grid, Card, etc.

class Question(models.Model):
    category = models.ForeignKey(Category, null=True)
    answer_type = models.ForeignKey(AnswerType, null=True)
    description = models.CharField(max_length=100)
    layout = models.CharField(max_length=100) # "1.4.2.1"

class AnswerType(models.Model):
    name = models.CharField(max_length=100) # Multiple Choice, Int, Address, Phone Num, etc.

class Answer(models.Model):
    question = models.ForeignKey(Question, null=True)
    answer_type = models.ForeignKey(AnswerType, null=True)
    value = models.CharField(max_length=100)
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
    category = models.ForeignKey(Category, null=True)
    language = models.ForeignKey(Language, null=True)
    text = models.CharField(max_length=100)

class AnswerTranslation(models.Model):
    answer = models.ForeignKey(Answer, null=True)
    language = models.ForeignKey(Language, null=True)
    text = models.CharField(max_length=100) # Longer?

class PromptTranslation(models.Model):
    prompt = models.ForeignKey(Prompt, null=True)
    language = models.ForeignKey(Language, null=True)
    text = models.CharField(max_length=100) # Longer?

class ConditionTranslation(models.Model):
    condition = models.ForeignKey(Condition, null=True)
    language = models.ForeignKey(Language, null=True)
    text = models.CharField(max_length=100) # Longer?
    # This would allow for a message to be displayed if condition is satisfied