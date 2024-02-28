from django.db import models
from django.db.models import JSONField

class InterceptionCache(models.Model):
    reference_date = models.DateField()
    interceptions = JSONField(null=True)
    