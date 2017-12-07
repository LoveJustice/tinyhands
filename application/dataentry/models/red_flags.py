from django.db import models

class RedFlags(models.Model):
    priority = models.PositiveIntegerField()
    field = models.CharField(max_length=100)
    text = models.CharField(max_length=256)