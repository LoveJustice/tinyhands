from django.db import models

from .border_station import BorderStation

class OperationsData(models.Model):
    year_month = models.PositiveIntegerField()
    station = station = models.ForeignKey(BorderStation)
    compliance = models.FloatField(null=True)
    budget = models.PositiveIntegerField(null=True)
    intercepts = models.PositiveIntegerField(null=True)
    arrests = models.PositiveIntegerField(null=True)
    gospel = models.PositiveIntegerField(null=True)
    empowerment = models.PositiveIntegerField(null=True)
    cifs = models.PositiveIntegerField(null=True)
    convictions = models.PositiveIntegerField(null=True)