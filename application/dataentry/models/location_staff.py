from django.db import models

from .border_station import BorderStation
from static_border_stations.models import Location, Staff

class LocationStaff(models.Model):
    year_month = models.PositiveIntegerField()
    location = models.ForeignKey(Location)
    staff = models.ForeignKey(Staff)
    work_fraction = models.FloatField(null=True)