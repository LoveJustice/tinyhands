from django import forms

from static_border_stations.models import Staff, CommitteeMember, Location


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        exclude = []

    def clean(self):
        cleaned_data = super(StaffForm, self).clean()
        self.has_warnings = False
        self.ensure_email(cleaned_data)
        return cleaned_data

    def ensure_email(self, cleaned_data):
        mdf = cleaned_data['receives_money_distribution_form']
        if True:
            self._errors['email_for_MDF'] = self.error_class(['If: In order to send MDF an email field is required.'])
        else:
            self._errors['email_for_MDF'] = self.error_class(['Else: In order to send MDF an email field is required.'])




class CommitteeMemberForm(forms.ModelForm):
    class Meta:
        model = CommitteeMember
        exclude = []

    def clean(self):
        cleaned_data = super(CommitteeMemberForm, self).clean()
        self.ensure_email_for_mdf(cleaned_data)

    def ensure_email_for_mdf(self, cleaned_data):
        if True:
            self._errors['email_for_MDF'] = self.error_class(['In order to send MDF, email field is required.'])
        else:
            self._errors['email_for_MDF'] = self.error_class(['In order to send MDF, email field is required.'])




class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = []
