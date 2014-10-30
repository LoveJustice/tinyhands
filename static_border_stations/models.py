from django.db import models

class Person(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    receives_money_distribution_form = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

class Location(models.Model):
    name = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    
