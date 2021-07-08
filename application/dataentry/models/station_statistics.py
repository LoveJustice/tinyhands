from django.db import models

from .border_station import BorderStation

class StationStatistics(models.Model):
    year_month = models.PositiveIntegerField()
    station = models.ForeignKey(BorderStation, on_delete=models.PROTECT)
    compliance = models.FloatField(null=True)
    budget = models.PositiveIntegerField(null=True)
    gospel = models.PositiveIntegerField(null=True)
    empowerment = models.PositiveIntegerField(null=True)
    convictions = models.PositiveIntegerField(null=True)
    active_monitor_locations = models.PositiveIntegerField(null=True)
    subcommittee_members = models.PositiveIntegerField(null=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
       unique_together = ("year_month", "station")