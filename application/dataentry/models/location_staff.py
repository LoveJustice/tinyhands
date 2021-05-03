from django.db import models

from .border_station import BorderStation
from static_border_stations.models import Location, Staff

class LocationStaff(models.Model):
    year_month = models.PositiveIntegerField()
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    work_fraction = models.FloatField(null=True)
    modified_date = models.DateTimeField(auto_now=True)