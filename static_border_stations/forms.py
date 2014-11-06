from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from static_border_stations.models import Person,Location

        
class StaffForm(forms.ModelForm):
    class Meta:
        model = Person
        title = 'Staff'
        
class CommitteeMemberForm(forms.ModelForm):
    class Meta:
        model = Person
        title = 'Committee Members'
        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location