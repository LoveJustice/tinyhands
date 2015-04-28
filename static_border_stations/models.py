from django.db import models
from dataentry.models import BorderStation


class Person(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    receives_money_distribution_form = models.BooleanField(default=False)
    border_station = models.ForeignKey(BorderStation, null=False, default=1)

    class Meta:
        abstract = True


class Staff(Person):
    class Meta:
        abstract = False



class CommitteeMember(Person):
    class Meta:
        abstract = False


class Location(models.Model):
    name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    border_station = models.ForeignKey(BorderStation, null=False, default=1)
