from django.db import models

from .border_station import BorderStation
from static_border_stations.models import Location

class LocationStatistics(models.Model):
    year_month = models.PositiveIntegerField()
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    intercepts = models.PositiveIntegerField(null=True)
    arrests = models.PositiveIntegerField(null=True)