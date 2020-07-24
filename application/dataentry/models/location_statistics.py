from django.db import models

from .border_station import BorderStation
from static_border_stations.models import Location

class LocationStatistics(models.Model):
    year_month = models.PositiveIntegerField()
    station = station = models.ForeignKey(BorderStation)
    location = models.ForeignKey(Location, null=True)
    intercepts = models.PositiveIntegerField(null=True)
    arrests = models.PositiveIntegerField(null=True)