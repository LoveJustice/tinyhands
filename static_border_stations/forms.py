from django import forms

from static_border_stations.models import Person, Staff, CommitteeMember, Location


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        exclude = []

    def clean(self):
        person_data = self.cleaned_data
	if "email" not in person_data:
            return
        if person_data['receives_money_distribution_form'] and not person_data['email']:
            raise forms.ValidationError("Email cannot be blank when receives money distribution form is checked.")


class StaffForm(PersonForm):
    class Meta:
        model = Staff
        exclude = []


class CommitteeMemberForm(PersonForm):
    class Meta:
        model = CommitteeMember
        exclude = []


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = []
