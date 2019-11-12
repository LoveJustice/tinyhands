from django.db import models
from django.contrib.postgres.fields import JSONField

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

    def __str__(self):
        return self.name