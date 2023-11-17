from django.db import models

class InterceptionCache(models.Model):
    reference_date = models.DateField()
    interceptions = models.JSONField(null=True)
    