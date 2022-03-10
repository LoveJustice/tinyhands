from django.db import models
from .border_station import BorderStation


class Gospel(models.Model):
    station = models.ForeignKey(BorderStation)
    date_time_entered_into_system = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)
    
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=4, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    staff_name = models.CharField(max_length=126, null=True)
    notes = models.TextField(blank=True)
    profession_date = models.DateField(null=True)
    