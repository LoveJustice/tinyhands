from django import forms
from django.db import models
from dataentry.models import (
    VictimInterview,
    InterceptionRecord,
    Interceptee,
    VictimInterviewPersonBox,
    VictimInterviewLocationBox
)
from django.forms.models import inlineformset_factory
from django.core.exceptions import ValidationError


class InterceptionRecordForm(forms.ModelForm):

    interception_type = forms.ChoiceField(
        choices=InterceptionRecord.INTERCEPT_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    contact_paid = forms.ChoiceField(
        choices=InterceptionRecord.BOOL_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    name_come_up_before = forms.ChoiceField(
        choices=InterceptionRecord.BOOL_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )

    class Meta:
        model = InterceptionRecord
        exclude = ['form_entered_by', 'date_form_received']

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


# Make all fields with choices radio selects
def make_choice_widgets_radio(f):
    if f.choices != []:
        print f.choices
        return forms.ChoiceField(choices=f.choices, widget=forms.RadioSelect, required=not f.blank)
    else:
        return f.formfield()


class VictimInterviewForm(forms.ModelForm):
    formfield_callback = make_choice_widgets_radio
    statement_read_before_beginning = forms.BooleanField(required=True)

    # These are needed so we can set required=True
    victim_recruited_in_village = forms.ChoiceField(choices=VictimInterview.BOOL_CHOICES, widget=forms.RadioSelect, required=True)
    victim_stayed_somewhere_between = forms.ChoiceField(choices=VictimInterview.BOOL_CHOICES, widget=forms.RadioSelect, required=True)
    victim_knew_details_about_destination = forms.ChoiceField(choices=VictimInterview.BOOL_CHOICES, widget=forms.RadioSelect, required=True)
    has_signature = forms.ChoiceField(choices=VictimInterview.BOOL_CHOICES, widget=forms.RadioSelect, required=True)

    class Meta:
        model = VictimInterview

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(VictimInterviewForm, self).clean()

        if not (
            cleaned_data.get('migration_plans_education') or
            cleaned_data.get('migration_plans_travel_tour') or
            cleaned_data.get('migration_plans_shopping') or
            cleaned_data.get('migration_plans_eloping') or
            cleaned_data.get('migration_plans_arranged_marriage') or
            cleaned_data.get('migration_plans_meet_own_family') or
            cleaned_data.get('migration_plans_visit_brokers_home') or
            cleaned_data.get('migration_plans_medical_treatment') or
            cleaned_data.get('migration_plans_job_broker_did_not_say') or
            cleaned_data.get('migration_plans_job_baby_care') or
            cleaned_data.get('migration_plans_job_factory') or
            cleaned_data.get('migration_plans_job_hotel') or
            cleaned_data.get('migration_plans_job_shop') or
            cleaned_data.get('migration_plans_job_laborer') or
            cleaned_data.get('migration_plans_job_brothel') or
            cleaned_data.get('migration_plans_job_household') or
            cleaned_data.get('migration_plans_job_other') or
            cleaned_data.get('migration_plans_job_value') or
            cleaned_data.get('migration_plans_other')
        ):
            self._errors['migration_plans_education'] = self.error_class(["At least one choice must be selected."])

        if not (
            cleaned_data.get('primary_motivation_support_myself') or
            cleaned_data.get('primary_motivation_support_family') or
            cleaned_data.get('primary_motivation_personal_debt') or
            cleaned_data.get('primary_motivation_family_debt') or
            cleaned_data.get('primary_motivation_love_marriage') or
            cleaned_data.get('primary_motivation_bad_home_marriage') or
            cleaned_data.get('primary_motivation_get_an_education') or
            cleaned_data.get('primary_motivation_tour_travel') or
            cleaned_data.get('primary_motivation_didnt_know') or
            cleaned_data.get('primary_motivation_other')
        ):
            self._errors['primary_motivation_support_myself'] = self.error_class(["At least one choice must be selected."])

        return cleaned_data


class VictimInterviewPersonBoxForm(forms.ModelForm):
    # This doesn't work with the extra_views CreateWithInlinesView sadly so we have to do it manually
    #formfield_callback = make_choice_widgets_radio

    gender = forms.ChoiceField(choices=VictimInterviewPersonBox.GENDER_CHOICES, widget=forms.RadioSelect, required=False)
    physical_description = forms.ChoiceField(choices=VictimInterviewPersonBox.PHYSICAL_DESCRIPTION_CHOICES, widget=forms.RadioSelect, required=False)
    occupation = forms.ChoiceField(choices=VictimInterviewPersonBox.OCCUPATION_CHOICES, widget=forms.RadioSelect, required=False)
    political_party = forms.ChoiceField(choices=VictimInterviewPersonBox.POLITICAL_PARTY_CHOICES, widget=forms.RadioSelect, required=False)
    associated_with_place = forms.ChoiceField(choices=VictimInterviewPersonBox.BOOL_CHOICES, widget=forms.RadioSelect, required=False)

    class Meta:
        model = VictimInterviewPersonBox

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewPersonBoxForm, self).__init__(*args, **kwargs)


class VictimInterviewLocationBoxForm(forms.ModelForm):
    associated_with_person = forms.ChoiceField(choices=VictimInterviewLocationBox.BOOL_CHOICES, widget=forms.RadioSelect, required=False)

    class Meta:
        model = VictimInterviewLocationBox

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewLocationBoxForm, self).__init__(*args, **kwargs)
