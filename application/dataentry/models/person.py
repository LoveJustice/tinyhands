from django.db import models

from addresses import Address1, Address2

class Person(models.Model):

    GENDER_CHOICES = [ ('M', 'm'), ('F', 'f'),]

    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    address1 = models.ForeignKey(Address1, null=True, blank=True)
    address2 = models.ForeignKey(Address2, null=True, blank=True)
    phone_contact = models.CharField(max_length=255, blank=True)
