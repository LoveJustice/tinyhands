from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from static_border_stations.models import Person,Location

        
class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location