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
    template = JSONField(null=True)
        # contains array of objects with section name and question count
        
    def get_form(self):
        form = Form.objects.get(form_name=self.form_name)
        return form
    
class AuditSample(models.Model):
    audit = models.ForeignKey(Audit)
    form_id = models.PositiveIntegerField()
    form_number = models.CharField(max_length=126)
    auditor = models.ForeignKey(Account, null=True, on_delete=models.SET_NULL)
    detail_notes = models.TextField(blank=True)
    high_level_notes = models.TextField(blank=True)
    completion_date = models.DateField(null=True)
    results = JSONField(null=True)
        # contains array of objects with section name incorrect count
    corrected = models.CharField(max_length=126)
    