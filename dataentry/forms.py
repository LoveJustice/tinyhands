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

# Django forms for some reason use 1,2,3 for values for NullBooleanField
BOOLEAN_CHOICES = [
    (False, 'No'),
    (True, 'Yes'),
]


def make_null_boolean_fields_radio(f):
    if isinstance(f, models.NullBooleanField):
        return forms.ChoiceField(choices=NULL_BOOLEAN_CHOICES, widget=forms.RadioSelect, initial=1)
    else:
        return f.formfield()


class InterceptionRecordForm(forms.ModelForm):
    #formfield_callback = make_null_boolean_fields_radio

    name_come_up_before_yes = forms.BooleanField()
    name_come_up_before_no = forms.BooleanField()
    name_come_up_before = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )


    interception_type = forms.MultipleChoiceField(
        choices=InterceptionRecord.INTERCEPT_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    ignore_warnings = forms.BooleanField(
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
                try:
                    model_field = InterceptionRecord._meta.get_field_by_name(field_name)[0]
                    if hasattr(model_field, 'weight'):
                        field.weight = model_field.weight
                except:
                    pass  # Don't worry about this for nonmodel fields like ignore_warnings

    def clean(self):
        cleaned_data = super(InterceptionRecordForm, self).clean()
        self.has_warnings = False

        self.at_least_one_box_checked_on_page_one(cleaned_data)
        self.box_six_or_seven_must_be_checked(cleaned_data)
        self.if_box_six_checked_at_least_one_from_six_one_to_six_nine_must_be_checked(cleaned_data)
        self.if_box_six_other_is_checked_the_other_value_must_be_present(cleaned_data)
        self.if_box_7_1_ensure_7_2(cleaned_data)
        self.if_contact_noticed_ensure_contact_paid(cleaned_data)
        self.if_8_2_ensure_number_specified(cleaned_data)

        if not cleaned_data.get('ignore_warnings'):
            self.ensure_some_red_flags_checked(cleaned_data)
            self.ensure_some_noticing_reason_checked(cleaned_data)
            self.ensure_8_1_2_3_checked(cleaned_data)
            self.ensure_at_least_one_of_9_1_through_9_5_are_checked(cleaned_data)
            self.ensure_signature_on_form(cleaned_data)

        return cleaned_data

    def at_least_one_box_checked_on_page_one(self, cleaned_data):
        if not (
            cleaned_data.get('who_in_group_alone') or
            cleaned_data.get('who_in_group_husbandwife') or
            cleaned_data.get('who_in_group_relative') or
            cleaned_data.get('drugged_or_drowsy') or
            cleaned_data.get('meeting_someone_across_border') or
            cleaned_data.get('seen_in_last_month_in_nepal') or
            cleaned_data.get('traveling_with_someone_not_with_her') or
            cleaned_data.get('wife_under_18') or
            cleaned_data.get('married_in_past_2_weeks') or
            cleaned_data.get('married_in_past_2_8_weeks') or
            cleaned_data.get('less_than_2_weeks_before_eloping') or
            cleaned_data.get('between_2_12_weeks_before_eloping') or
            cleaned_data.get('caste_not_same_as_relative') or
            cleaned_data.get('caught_in_lie') or
            cleaned_data.get('other_red_flag') or
            cleaned_data.get('other_red_flag_value') or
            cleaned_data.get('where_going_job') or
            cleaned_data.get('where_going_visit') or
            cleaned_data.get('where_going_shopping') or
            cleaned_data.get('where_going_study') or
            cleaned_data.get('where_going_treatment') or
            cleaned_data.get('doesnt_know_going_to_india') or
            cleaned_data.get('running_away_over_18') or
            cleaned_data.get('running_away_under_18') or
            cleaned_data.get('going_to_gulf_for_work') or
            cleaned_data.get('no_address_in_india') or
            cleaned_data.get('no_company_phone') or
            cleaned_data.get('no_appointment_letter') or
            cleaned_data.get('valid_gulf_country_visa') or
            cleaned_data.get('passport_with_broker') or
            cleaned_data.get('job_too_good_to_be_true') or
            cleaned_data.get('not_real_job') or
            cleaned_data.get('couldnt_confirm_job') or
            cleaned_data.get('no_bags_long_trip') or
            cleaned_data.get('shopping_overnight_stuff_in_bags') or
            cleaned_data.get('no_enrollment_docs') or
            cleaned_data.get('doesnt_know_school_name') or
            cleaned_data.get('no_school_phone') or
            cleaned_data.get('not_enrolled_in_school') or
            cleaned_data.get('reluctant_treatment_info') or
            cleaned_data.get('no_medical_documents') or
            cleaned_data.get('fake_medical_documents') or
            cleaned_data.get('no_medical_appointment')
        ):
            self._errors['who_in_group_alone'] = self.error_class(['At least one choice must be selected.'])

    def box_six_or_seven_must_be_checked(self, cleaned_data):
        if not (
                cleaned_data.get('contact_noticed') or
                cleaned_data.get('staff_noticed')
        ):
            self._errors['contact_noticed'] = self.error_class(['Either Contact (6.0) or Staff (7.0) must be chosen for how interception was made.'])

    def if_box_six_checked_at_least_one_from_six_one_to_six_nine_must_be_checked(self, cleaned_data):
        if cleaned_data.get('contact_noticed') and not (
            cleaned_data.get('contact_hotel_owner') or
            cleaned_data.get('contact_rickshaw_driver') or
            cleaned_data.get('contact_taxi_driver') or
            cleaned_data.get('contact_bus_driver') or
            cleaned_data.get('contact_church_member') or
            cleaned_data.get('contact_other_ngo') or
            cleaned_data.get('contact_police') or
            cleaned_data.get('contact_subcommittee_member') or
            cleaned_data.get('contact_other')
        ):
            self._errors['contact_noticed'] = self.error_class(
                ['Contact (6.0) chosen for how interception was made, but a specific kind was not specified (6.1-6.9).'])

    def if_box_six_other_is_checked_the_other_value_must_be_present(self, cleaned_data):
        if cleaned_data.get('contact_other') and not cleaned_data.get('contact_other_value'):
            self._errors['contact_other_value'] = self.error_class(
                ['Other chosen for Contact but the kind is not specified.'])

    def if_contact_noticed_ensure_contact_paid(self, cleaned_data):
        if cleaned_data.get('contact_noticed') and not cleaned_data.get('contact_paid'):
            self._errors['contact_paid'] = self.error_class(
                ['Contact noticed chosen but paid not specified.'])

    def if_8_2_ensure_number_specified(self, cleaned_data):
        if cleaned_data.get('name_come_up_before') and not cleaned_data.get('name_come_up_before_yes_value'):
            self._errors['name_come_up_before_yes_value'] = self.error_class(
                ['Name came up specified but no number given.'])

    def if_box_7_1_ensure_7_2(self, cleaned_data):
        if cleaned_data.get('staff_noticed') and not cleaned_data.get('staff_who_noticed'):
            self._errors['staff_who_noticed'] = self.error_class(
                ['Staff noticed chosen but name not specified.'])

    def ensure_some_red_flags_checked(self, cleaned_data):
        if not (
            cleaned_data.get('drugged_or_drowsy') or
            cleaned_data.get('meeting_someone_across_border') or
            cleaned_data.get('seen_in_last_month_in_nepal') or
            cleaned_data.get('traveling_with_someone_not_with_her') or
            cleaned_data.get('wife_under_18') or
            cleaned_data.get('married_in_past_2_weeks') or
            cleaned_data.get('married_in_past_2_8_weeks') or
            cleaned_data.get('less_than_2_weeks_before_eloping') or
            cleaned_data.get('between_2_12_weeks_before_eloping') or
            cleaned_data.get('caste_not_same_as_relative') or
            cleaned_data.get('caught_in_lie') or
            cleaned_data.get('other_red_flag') or
            cleaned_data.get('doesnt_know_going_to_india') or
            cleaned_data.get('running_away_over_18') or
            cleaned_data.get('running_away_under_18') or
            cleaned_data.get('going_to_gulf_for_work') or
            cleaned_data.get('no_address_in_india') or
            cleaned_data.get('no_company_phone') or
            cleaned_data.get('no_appointment_letter') or
            cleaned_data.get('valid_gulf_country_visa') or
            cleaned_data.get('passport_with_broker') or
            cleaned_data.get('job_too_good_to_be_true') or
            cleaned_data.get('not_real_job') or
            cleaned_data.get('couldnt_confirm_job') or
            cleaned_data.get('no_bags_long_trip') or
            cleaned_data.get('shopping_overnight_stuff_in_bags') or
            cleaned_data.get('no_enrollment_docs') or
            cleaned_data.get('doesnt_know_school_name') or
            cleaned_data.get('no_school_phone') or
            cleaned_data.get('not_enrolled_in_school') or
            cleaned_data.get('reluctant_treatment_info') or
            cleaned_data.get('no_medical_documents') or
            cleaned_data.get('fake_medical_documents') or
            cleaned_data.get('no_medical_appointment') or
            cleaned_data.get('doesnt_know_villiage_details') or
            cleaned_data.get('reluctant_villiage_info') or
            cleaned_data.get('reluctant_family_info') or
            cleaned_data.get('refuses_family_info') or
            cleaned_data.get('under_18_cant_contact_family') or
            cleaned_data.get('under_18_family_doesnt_know') or
            cleaned_data.get('under_18_family_unwilling') or
            cleaned_data.get('over_18_family_doesnt_know') or
            cleaned_data.get('over_18_family_unwilling')
        ):
            error = self.error_class(['No red flags are checked.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['drugged_or_drowsy'] = error

    def ensure_some_noticing_reason_checked(self, cleaned_data):
        if cleaned_data.get('staff_noticed') and not (
            cleaned_data.get('noticed_hesitant') or
            cleaned_data.get('noticed_nervous_or_afraid') or
            cleaned_data.get('noticed_hurrying') or
            cleaned_data.get('noticed_drugged_or_drowsy') or
            cleaned_data.get('noticed_new_clothes') or
            cleaned_data.get('noticed_dirty_clothes') or
            cleaned_data.get('noticed_carrying_full_bags') or
            cleaned_data.get('noticed_village_dress') or
            cleaned_data.get('noticed_indian_looking') or
            cleaned_data.get('noticed_typical_village_look') or
            cleaned_data.get('noticed_looked_like_agent') or
            cleaned_data.get('noticed_caste_difference') or
            cleaned_data.get('noticed_young_looking') or
            cleaned_data.get('noticed_waiting_sitting') or
            cleaned_data.get('noticed_walking_to_border') or
            cleaned_data.get('noticed_roaming_around') or
            cleaned_data.get('noticed_exiting_vehicle') or
            cleaned_data.get('noticed_heading_to_vehicle') or
            cleaned_data.get('noticed_in_a_vehicle') or
            cleaned_data.get('noticed_in_a_rickshaw') or
            cleaned_data.get('noticed_in_a_cart') or
            cleaned_data.get('noticed_carrying_a_baby') or
            cleaned_data.get('noticed_on_the_phone') or
            cleaned_data.get('noticed_other_sign')
        ):
            error = self.error_class(['Staff Noticed (7.0) is checked, but no reason is checked (7.2 - 7.25).'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['staff_noticed'] = error

    def ensure_8_1_2_3_checked(self, cleaned_data):
        if not cleaned_data.get('call_subcommittee_chair'):
            error = self.error_class(['Procedure not followed.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['call_subcommittee_chair'] = error

        if not cleaned_data.get('call_thn_to_cross_check'):
            error = self.error_class(['Procedure not followed.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['call_thn_to_cross_check'] = error

        if not cleaned_data.get('scan_and_submit_same_day'):
            error = self.error_class(['Procedure not followed.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['scan_and_submit_same_day'] = error

    def ensure_at_least_one_of_9_1_through_9_5_are_checked(self, cleaned_data):
        if not cleaned_data.get('interception_type'):
            error = self.error_class(['Field should be included, though not required.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['interception_type'] = error

    def ensure_signature_on_form(self, cleaned_data):
        if not cleaned_data.get('has_signature'):
            error = self.error_class(['Form should be signed, though not required.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['has_signature'] = error


IntercepteeFormSet = inlineformset_factory(InterceptionRecord, Interceptee, extra=12)


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
    victim_recruited_in_village = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.RadioSelect, required=True)
    victim_stayed_somewhere_between = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.RadioSelect, required=True)
    victim_knew_details_about_destination = forms.ChoiceField(choices=BOOLEAN_CHOICES, widget=forms.RadioSelect, required=True)

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

        if not cleaned_data.get('has_signature'):
            self._errors['has_signature'] = self.error_class(["The form must be signed."])

        return cleaned_data


class VictimInterviewPersonBoxForm(forms.ModelForm):
    # This doesn't work with the extra_views CreateWithInlinesView sadly so we have to do it manually
    #formfield_callback = make_choice_widgets_radio

    gender = forms.ChoiceField(choices=VictimInterviewPersonBox.GENDER_CHOICES, widget=forms.RadioSelect, required=False)
    physical_description = forms.ChoiceField(choices=VictimInterviewPersonBox.PHYSICAL_DESCRIPTION_CHOICES, widget=forms.RadioSelect, required=False)
    occupation = forms.ChoiceField(choices=VictimInterviewPersonBox.OCCUPATION_CHOICES, widget=forms.RadioSelect, required=False)
    political_party = forms.ChoiceField(choices=VictimInterviewPersonBox.POLITICAL_PARTY_CHOICES, widget=forms.RadioSelect, required=False)
    associated_with_place = forms.ChoiceField(widget=forms.RadioSelect, required=False)

    class Meta:
        model = VictimInterviewPersonBox

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewPersonBoxForm, self).__init__(*args, **kwargs)


class VictimInterviewLocationBoxForm(forms.ModelForm):
    associated_with_person = forms.ChoiceField(widget=forms.RadioSelect, required=False)

    class Meta:
        model = VictimInterviewLocationBox

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewLocationBoxForm, self).__init__(*args, **kwargs)
