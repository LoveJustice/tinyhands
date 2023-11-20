from django.db import models
from .country import Country

class Holiday(models.Model):
    country = models.ForeignKey(Country)
    name = models.CharField(max_length=127)
    holiday = models.DateField(null=False)