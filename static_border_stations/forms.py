from django import forms

from static_border_stations.models import Staff, CommitteeMember, Location


class PersonForm(forms.ModelForm):

    def clean(self):
        person_data = self.cleaned_data
        if person_data['receives_money_distribution_form'] and not person_data['email']:
            raise forms.ValidationError("foo")


class StaffForm(PersonForm):
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
