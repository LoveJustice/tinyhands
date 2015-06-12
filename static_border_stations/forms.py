from django import forms

from static_border_stations.models import Staff, CommitteeMember, Location


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        exclude = []
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False

class CommitteeMemberForm(forms.ModelForm):
    email = forms.EmailField(max_length=255, unique=True, required=False)
    class Meta:
        model = CommitteeMember
        exclude = ['email']


class LocationForm(forms.ModelForm):
    email = forms.EmailField(max_length=255, unique=True, required=False)
    class Meta:
        model = Location
        exclude = ['email']