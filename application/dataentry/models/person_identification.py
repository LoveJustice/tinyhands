from django.db import models
from .person import Person

class PersonIdentification(models.Model):
	type = models.CharField(max_length=255)
	number = models.CharField(max_length=255)
	location = models.CharField(max_length=255, null=True, blank=True)
	person = models.ForeignKey(Person)