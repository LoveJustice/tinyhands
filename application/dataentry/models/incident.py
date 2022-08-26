from django.db import models

from .form import BaseForm

class Incident(BaseForm):
    incident_number = models.CharField('Incident #:', max_length=20, unique=True)
    incident_date = models.DateField('Incident date')
    summary = models.TextField(blank=True)