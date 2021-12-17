from django.db import models
from django.contrib.postgres.fields import JSONField

from .form import Form
from .country import Country
from accounts.models import Account

class Audit(models.Model):
    form_name = models.CharField(max_length=126)
    country = models.ForeignKey(Country)
    start_date = models.DateField()
    end_date = models.DateField()
    percent_to_sample = models.FloatField(100)
    author = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    forms_in_range = models.PositiveIntegerField(null=True)
    template = JSONField(null=True)
    form_version = models.CharField(max_length=126, blank=True)
        # contains array of objects with section name and question count
        
    def get_form(self):
        form = Form.objects.get(form_name=self.form_name)
        return form
    
    def get_question_count(self):
        questions = 0
        for section in self.template:
            if section['questions']:
                questions += section['questions']
        return questions
    
    def get_samples_complete(self):
        return AuditSample.objects.filter(audit=self, completion_date__isnull=False).count()
    
    def get_sample_count(self):
        return AuditSample.objects.filter(audit=self).count()
    
    def get_total_incorrect(self):
        completed = AuditSample.objects.filter(audit=self).exclude(completion_date__isnull=True)
        total_incorrect = 0
        for sample in completed:
            for value in sample.results.values():
                if value is not None:
                    total_incorrect += value
        return total_incorrect
    
    def accuracy(self):
        result = '-'
        total_questions = self.get_question_count() * self.get_samples_complete()
        if total_questions > 0:
            result = round((total_questions - self.get_total_incorrect()) * 100 / total_questions, 1)
        return result
    
class AuditSample(models.Model):
    audit = models.ForeignKey(Audit)
    form_id = models.PositiveIntegerField()
    form_number = models.CharField(max_length=126)
    auditor = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    detail_notes = models.TextField(blank=True)     # AKA auditor notes
    high_level_notes = models.TextField(blank=True)
    monitor_notes = models.TextField(blank=True)
    completion_date = models.DateField(null=True)
    results = JSONField(null=True)
        # contains array of objects with section name incorrect count
    corrected = models.CharField(max_length=126)
    no_paper_form = models.BooleanField('No Paper form', default=False)
    