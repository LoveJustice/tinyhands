from django.db import models

class ClientDiagnostic(models.Model):
    user_name = models.CharField(max_length=100)
    diagnostic_date = models.DateField(auto_now_add=True)
    location = models.TextField(blank=True)
    diagnostic_data = models.TextField(blank=True)