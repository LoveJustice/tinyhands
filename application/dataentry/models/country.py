from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom_level = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=127, blank=True)
    mdf_sender_email = models.CharField(max_length=127)

    def __str__(self):
        return self.name