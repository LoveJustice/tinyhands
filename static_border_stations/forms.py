from django import forms
from django.db import models
from django.core.exceptions import ValidationError

from static_border_stations.models import Staff,CommitteeMember,Location
        
class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
       	exclude = []

class CommitteeMemberForm(forms.ModelForm):
    class Meta:
        model = CommitteeMember
        exclude = []
        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = []