from django.db import models

class InterceptionAlert(models.Model):
    json = models.CharField('json', max_length=8192)
    created = models.DateTimeField(auto_now_add=True)