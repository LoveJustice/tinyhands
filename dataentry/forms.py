from django import forms
from dataentry.models import InterceptionRecord, Interceptee, VictimInterview
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError


class InterceptionRecordForm(forms.ModelForm):

    interception_type = forms.ChoiceField(
        choices=InterceptionRecord.INTERCEPT_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    class Meta:
        model = InterceptionRecord

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('label_suffix', '')
        super(InterceptionRecordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.iteritems():

            if type(field) == forms.fields.BooleanField:
                model_field = InterceptionRecord._meta.get_field_by_name(field_name)[0]
                if hasattr(model_field, 'weight'):
                    field.weight = model_field.weight

    def clean_who_in_group_alone(self):
        if not (
            self.cleaned_data.get('who_in_group_alone') or
            self.cleaned_data.get('who_in_group_husbandwife') or
            self.cleaned_data.get('who_in_group_relative') or
            self.cleaned_data.get('drugged_or_drowsy') or
            self.cleaned_data.get('meeting_someone_across_border') or
            self.cleaned_data.get('seen_in_last_month_in_nepal') or
            self.cleaned_data.get('traveling_with_someone_not_with_her') or
            self.cleaned_data.get('wife_under_18') or
            self.cleaned_data.get('married_in_past_2_weeks') or
            self.cleaned_data.get('married_in_past_2_8_weeks') or
            self.cleaned_data.get('less_than_2_weeks_before_eloping') or
            self.cleaned_data.get('between_2_12_weeks_before_eloping') or
            self.cleaned_data.get('caste_not_same_as_relative') or
            self.cleaned_data.get('caught_in_lie') or
            self.cleaned_data.get('other_red_flag') or
            self.cleaned_data.get('other_red_flag_value') or
            self.cleaned_data.get('where_going_job') or
            self.cleaned_data.get('where_going_visit') or
            self.cleaned_data.get('where_going_shopping') or
            self.cleaned_data.get('where_going_study') or
            self.cleaned_data.get('where_going_treatment') or
            self.cleaned_data.get('doesnt_know_going_to_india') or
            self.cleaned_data.get('running_away_over_18') or
            self.cleaned_data.get('running_away_under_18') or
            self.cleaned_data.get('going_to_gulf_for_work') or
            self.cleaned_data.get('no_address_in_india') or
            self.cleaned_data.get('no_company_phone') or
            self.cleaned_data.get('no_appointment_letter') or
            self.cleaned_data.get('valid_gulf_country_visa') or
            self.cleaned_data.get('passport_with_broker') or
            self.cleaned_data.get('job_too_good_to_be_true') or
            self.cleaned_data.get('not_real_job') or
            self.cleaned_data.get('couldnt_confirm_job') or
            self.cleaned_data.get('no_bags_long_trip') or
            self.cleaned_data.get('shopping_overnight_stuff_in_bags') or
            self.cleaned_data.get('no_enrollment_docs') or
            self.cleaned_data.get('doesnt_know_school_name') or
            self.cleaned_data.get('no_school_phone') or
            self.cleaned_data.get('not_enrolled_in_school') or
            self.cleaned_data.get('reluctant_treatment_info') or
            self.cleaned_data.get('no_medical_documents') or
            self.cleaned_data.get('fake_medical_documents') or
            self.cleaned_data.get('no_medical_appointment')
        ):
            raise ValidationError("Nothing on the first page of the form is filled out.")
        return self.cleaned_data.get('who_in_group_alone')

    def clean_contact_noticed(self):
        if not (
                self.cleaned_data.get('contact_noticed') or
                self.cleaned_data.get('staff_noticed')
        ):
            raise ValidationError("Either Contact (6.0) or Staff (7.0) must be chosen for how interception was made.")
        return self.cleaned_data.get('contact_noticed')

    def clean_contact_hotel_owner(self):
        print self.cleaned_data.get('contact_noticed')
        print self.cleaned_data.get('contact_hotel_owner')
        print self.cleaned_data.get('contact_rickshaw_driver')
        print self.cleaned_data.get('contact_taxi_driver')
        print self.cleaned_data.get('contact_bus_driver')
        print self.cleaned_data.get('contact_church_member')
        print self.cleaned_data.get('contact_other_ngo')
        print self.cleaned_data.get('contact_police')
        print self.cleaned_data.get('contact_subcommittee_member')
        print self.cleaned_data.get('contact_other')

        if self.cleaned_data.get('contact_noticed') and not (
            self.cleaned_data.get('contact_hotel_owner') or
            self.cleaned_data.get('contact_rickshaw_driver') or
            self.cleaned_data.get('contact_taxi_driver') or
            self.cleaned_data.get('contact_bus_driver') or
            self.cleaned_data.get('contact_church_member') or
            self.cleaned_data.get('contact_other_ngo') or
            self.cleaned_data.get('contact_police') or
            self.cleaned_data.get('contact_subcommittee_member') or
            self.cleaned_data.get('contact_other')
        ):
            raise ValidationError("Contact (6.0) chosen for how interception was made, but a specific kind was not specified (6.1-6.9).")
        return self.cleaned_data.get('contact_hotel_owner')


IntercepteeFormSet = inlineformset_factory(InterceptionRecord, Interceptee, extra=12)

#  self.cleaned_data.get('contact_other_value') or
#  self.cleaned_data.get('contact_paid_no') or
#  self.cleaned_data.get('contact_paid_yes') or
#  self.cleaned_data.get('contact_paid_how_much')


class VictimInterviewForm(forms.ModelForm):

    class Meta:
        model = VictimInterview
        widgets = {
            'victim_gender': forms.RadioSelect,
            'victim_caste': forms.RadioSelect,
            'victim_occupation': forms.RadioSelect,
            'victim_marital_status': forms.RadioSelect,
            'victim_primary_guardian': forms.RadioSelect,
            'victim_parents_marital_status': forms.RadioSelect,
            'victim_education_level': forms.RadioSelect,
            'victim_is_literate': forms.RadioSelect,
        }
