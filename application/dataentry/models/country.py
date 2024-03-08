from django.db import models
from django.db.models import JSONField

from .region import Region

class Country(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom_level = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=127, blank=True)
    mdf_sender_email = models.CharField(max_length=127)
    verification_start_year = models.PositiveIntegerField(null=True)
    verification_start_month = models.PositiveIntegerField(null=True)
    verification_goals = JSONField(null=True)
    options = JSONField(null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    prior_intercepts = models.IntegerField(default=0)
    prior_arrests = models.IntegerField(default=0)
    prior_convictions = models.IntegerField(default=0)
    enable_all_locations = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name

class CountryExchange(models.Model):
    year_month = models.PositiveIntegerField()
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    exchange_rate = models.FloatField(default=1)
    date_time_last_updated = models.DateTimeField(auto_now=True)