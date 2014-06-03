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
from django.utils.html import mark_safe


""" In this form we have three types of problem fields:

1. Boolean Fields that must be rendered as Yes/No checkboxes and allow users to
only select one and uncheck their answer if it is optional

2. Sets of checkboxes that must be constrained to a certain number of choices

3. 
"""


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


class VictimInterviewForm(forms.ModelForm):
    victim_gender = forms.ChoiceField(
        choices=VictimInterview.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    victim_is_literate = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    manpower_involved = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_recruited_in_village = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    victim_first_time_crossing_border = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_stayed_somewhere_between = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    victim_was_hidden = forms.MultipleChoiceField(
        choices=[(False, 'No'), (True, mark_safe('Yes <br/> Explain'))],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    victim_was_free_to_go_out = forms.MultipleChoiceField(
        choices=[(False, mark_safe('No <br/> Explain')), (True, 'Yes')],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_passport_with_broker = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    companion_with_when_intercepted = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    planning_to_meet_companion_later = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_knew_details_about_destination = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    other_involved_person_in_india = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_involved_husband_trafficker = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_involved_someone_met_along_the_way = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_involved_someone_involved_in_trafficking = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_involved_place_involved_in_trafficking = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_has_worked_in_sex_industry = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_place_worked_involved_sending_girls_overseas = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    """
    AWARENESS_CHOICES = [
        ('Had heard, but never knew how bad it was until I was intercepted by TH', 'Had heard, but never knew how bad it was until I was intercepted by TH'),
        ('Knew how bad it was, but didn\'t think that was happening to her', 'Knew how bad it was, but didn\'t think that was happening to her'),
        ('Had never heard about it', 'Had never heard about it'),
    ]
    awareness_before_interception = forms.MultipleChoiceField(
        choices=AWARENESS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    ATTITUDE_CHOICES = [
        ('Yes, thankful to TH for saving her', 'Yes, thankful to TH for saving her'),
        ('No, blames Tiny Hands for stopping her', 'No, blames Tiny Hands for stopping her'),
        ('Doesn\'t know', 'Doesn\'t Know'),
    ]
    attitude_towards_tiny_hands = forms.MultipleChoiceField(
        choices=AWARENESS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    GOSPEL_HEARD_CHOICES = [
        ('No, I have never heard', 'No, I have never heard'),
        ('Has heard the name only', 'Has heard the name only'),
        ('Had heard the gospel but never believed', 'Had heard the gospel but never believed'),
        ('Was already a believer', 'Was already a believer'),
    ]
    victim_heard_gospel = forms.MultipleChoiceField(
        choices=GOSPEL_HEARD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    VICTIM_BELIEFS_NOW_CHOICES = [
        ('Doesn\'t believe in Jesus', 'Doesn\'t believe in Jesus'),
        ('Believes in Jesus, but doesn\'t plan to go to church', 'Believes in Jesus, but doesn\'t plan to go to church'),
        ('Believes in Jesus and plans to go to church', 'Believes in Jesus and plans to go to church'),
    ]
    victim_beliefs_now = forms.MultipleChoiceField(
        choices=VICTIM_BELIEFS_NOW_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    guardian_knew_was_travelling_to_india = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    family_pressured_victim = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    family_will_try_sending_again = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_feels_safe_at_home = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_wants_to_go_home = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    VICTIM_ABUSE_CHOICES = [
        ('Never', 'Never'),
        ('Rarely / Minor', 'Rarely / Minor'),
        ('Frequent / Severe', 'Frequent / Severe'),
    ]
    victim_home_had_sexual_abuse = forms.MultipleChoiceField(
        choices=VICTIM_ABUSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_home_had_physical_abuse = forms.MultipleChoiceField(
        choices=VICTIM_ABUSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_home_had_emotional_abuse = forms.MultipleChoiceField(
        choices=VICTIM_ABUSE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    GUARDIAN_FREQUENCY_CHOICES = [
        ('Never', 'Never'),
        ('Occasionally', 'Occasionally'),
        ('All the time', 'All the time'),
    ]
    victim_guardian_drinks_alcohol = forms.MultipleChoiceField(
        choices=GUARDIAN_FREQUENCY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_guardian_uses_drugs = forms.MultipleChoiceField(
        choices=GUARDIAN_FREQUENCY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    ECONOMIC_SITUATION_CHOICES = [
        ('Unable to meet basic needs', 'Unable to meet basic needs'),
        ('Able to meet only basic needs, but it is very difficult', 'Able to meet only basic needs, but it is very difficult'),
        ('Comfortably meet basic needs, and can afford to buy some non-essential goods/services', 'Comfortably meet basic needs, and can afford to buy some non-essential goods/services'),
        ('Wealthy', 'Wealthy'),
    ]
    victim_family_economic_situation = forms.MultipleChoiceField(
        choices=ECONOMIC_SITUATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    victim_had_suicidal_thoughts = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    LEGAL_ACTION_CHOICES = [
        ('No', 'No'),
        ('FIR filed against', 'FIR filed against'),
        ('DoFE complaint against', 'DoFE complaint against'),
    ]
    legal_action_against_traffickers = forms.MultipleChoiceField(
        choices=LEGAL_ACTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    REASON_NO_LEGAL_CHOICES = [
        ('No trafficking suspected', 'No trafficking suspected'),
        ('Police say not enough information', 'Police say not enough information'),
        ('Trafficker is victim\'s own people', 'Trafficker is victim\'s own people'),
        ('She was going herself', 'She was going herself'),
        ('Trafficker ran away', 'Trafficker ran away'),
        ('Victim afraid of reputation', 'Victim afraid of reputation'),
        ('Victim afraid for her safety', 'Victim afraid for her safety'),
        ('Family afraid of reputation', 'Family afraid of reputation'),
        ('Family afraid for her safety', 'Family afraid for her safety'),
        ('Police bribed by trafficker', 'Police bribed by trafficker'),
        ('Victim / family bribed by trafficker', 'Victim / family bribed by trafficker'),
        ('Interference by powerful people', 'Interference by powerful people'),
        ('Other', 'Other'),
    ]
    reason_no_legal = forms.MultipleChoiceField(
        choices=REASON_NO_LEGAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    INTERVIEWER_RECOMMENDATION_CHOICES = [
        ('Plan to send the girl home to stay with her guardians', 'Plan to send the girl home to stay with her guardians'),
        ('Plan to send the girl to stay with other relatives', 'Plan to send the girl to stay with other relatives'),
        ('Tiny Hands needs to help her find another place to go', 'Tiny Hands needs to help her find another place to go'),
    ]
    interviewer_recommendation = forms.MultipleChoiceField(
        choices=INTERVIEWER_RECOMMENDATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_people_and_places_involved = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    """

    class Meta:
        model = VictimInterview

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(VictimInterviewForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            if (
                isinstance(field.widget, forms.CheckboxSelectMultiple) and
                field.choices == BOOLEAN_CHOICES
            ):
                initial = self.initial.get(field_name)
                if initial is not None:
                    self.initial[field_name] = [unicode(initial)]

    def clean(self):
        cleaned_data = super(VictimInterviewForm, self).clean()

        for field_name in cleaned_data.keys():
            field = self.fields[field_name]
            if (
                isinstance(field.widget, forms.CheckboxSelectMultiple) and
                field.choices == BOOLEAN_CHOICES
            ):
                if len(cleaned_data[field_name]) > 0:
                    cleaned_data[field_name] = bool(cleaned_data[field_name][0])
                else:
                    cleaned_data[field_name] = None

        for field_name_start in [
            'primary_motivation',
            'migration_plans',
            'victim_where_going',
        ]:
            if not self.at_least_one_checked(cleaned_data, field_name_start):
                self._errors[field_name_start] = self.error_class(['One box must be checked.'])

        return cleaned_data

    def at_least_one_checked(self, cleaned_data, field_name_start):
        for field_name in cleaned_data.keys():
            if field_name.startswith(field_name_start):
                if isinstance(self.fields[field_name].widget, forms.CheckboxInput):
                    if cleaned_data[field_name]:
                        return True
        return False


class VictimInterviewPersonBoxForm(forms.ModelForm):
    WHO_IS_THIS_CHOICES = [
        ('boss of...', 'boss of...'),
        ('co-worker of...', 'co-worker of...'),
        ('own relative of...', 'own relative of...'),
    ]
    who_is_this_relationship = forms.MultipleChoiceField(
        choices=WHO_IS_THIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    WHO_IS_THIS_ROLE_CHOICES = [
        ('Broker', 'Broker'),
        ('Companion', 'Companion'),
        ('India Trafficker', 'India Trafficker'),
        ('Contact of Husband', 'Contact of Husband'),
        ('Known Trafficker', 'Known Trafficker'),
        ('Manpower', 'Manpower'),
        ('Passport', 'Passport'),
        ('Sex Industry', 'Sex Industry'),
    ]
    who_is_this_role = forms.MultipleChoiceField(
        choices=WHO_IS_THIS_ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    gender = forms.MultipleChoiceField(
        choices=VictimInterviewPersonBox.GENDER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    PHYSICAL_DESCRIPTION_CHOICES = [
        ('Kirat', 'Kirat'),
        ('Sherpa', 'Sherpa'),
        ('Madeshi', 'Madeshi'),
        ('Pahadi', 'Pahadi'),
        ('Newari', 'Newari'),
    ]
    physical_description = forms.MultipleChoiceField(
        choices=PHYSICAL_DESCRIPTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    OCCUPATION_CHOICES = [
        ('None', 'None'),
        ('Agent (taking girls to India)', 'Agent (taking girls to India)'),
        ('Business owner', 'Business owner'),
        ('Other', 'Other'),
        ('Wage labor', 'Wage labor'),
        ('Job in India', 'Job in India'),
        ('Job in Gulf', 'Job in Gulf'),
        ('Farmer', 'Farmer'),
        ('Teacher', 'Teacher'),
        ('Police', 'Police'),
        ('Army', 'Army'),
        ('Guard', 'Guard'),
        ('Cook', 'Cook'),
        ('Driver', 'Driver'),
    ]
    occupation = forms.MultipleChoiceField(
        choices=OCCUPATION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    POLITICAL_PARTY_CHOICES = [
        ('Congress', 'Congress'),
        ('Maoist', 'Maoist'),
        ('UMN', 'UMN'),
        ('Forum', 'Forum'),
        ('Tarai Madesh', 'Tarai Madesh'),
        ('Shadbawona', 'Shadbawona'),
        ('Raprapha Nepal Thruhat', 'Raprapha Nepal Thruhat'),
        ('Nepal Janadikarik Forum', 'Nepal Janadikarik Forum'),
        ('Loktantrak Party', 'Loktantrak Party'),
        ('Don\'t Know', 'Don\'t Know'),
        ('Other', 'Other'),
    ]
    political_party = forms.MultipleChoiceField(
        choices=POLITICAL_PARTY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    INTERVIEWER_BELIEVES_CHOICES = [
        ('Interviewer believes they have definitely trafficked many girls', 'Interviewer believes they have definitely trafficked many girls'),
        ('Interviewer believes they have trafficked some girls', 'Interviewer believes they have trafficked some girls'),
        ('Interviewer suspects they are a trafficker', 'Interviewer suspects they are a trafficker'),
        ('Interviewer doesn\'t believe they are a trafficker', 'Interviewer doesn\'t believe they are a trafficker'),
    ]
    interviewer_believes = forms.MultipleChoiceField(
        choices=INTERVIEWER_BELIEVES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    VICTIM_BELIEVES_CHOICES = [
        ('Victim believes this location is definitely used to traffic many victims', 'Victim believes this location is definitely used to traffic many victims'),
        ('Victim believes this location has been used repeatedly to traffic some victims', 'Victim believes this location has been used repeatedly to traffic some victims'),
        ('Victim suspects this location has been used for trafficking', 'Victim suspects this location has been used for trafficking'),
        ('Victim does not believe this location is used for trafficking', 'Victim does not believe this location is used for trafficking'),
    ]
    victim_believes = forms.MultipleChoiceField(
        choices=VICTIM_BELIEVES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


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
