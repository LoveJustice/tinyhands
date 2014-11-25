from django import forms
from dataentry.models import BorderStation

from static_border_stations.models import Staff, CommitteeMember, Location


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff


class CommitteeMemberForm(forms.ModelForm):
    class Meta:
        model = CommitteeMember
        exclude = []


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = []