from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import inlineformset_factory
from django.utils.html import mark_safe

from .models import (BorderStation, District,
                     Interceptee, InterceptionRecord,
                     VDC,
                     VictimInterviewLocationBox, VictimInterviewPersonBox, VictimInterview)
from .fields import DistrictField, VDCField, FormNumberField

from accounts.models import Alert

BOOLEAN_CHOICES = [
    (False, 'No'),
    (True, 'Yes'),
]

class DreamSuitePaperForm(forms.ModelForm):
    class Meta:
        model = VictimInterview
        exclude = []

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(DreamSuitePaperForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields[field_name]
            if (
                isinstance(field.widget, forms.CheckboxSelectMultiple) and
                field.choices == BOOLEAN_CHOICES
                or
                field_name == 'victim_was_hidden' or
                field_name == 'victim_was_free_to_go_out'
            ):
                initial = self.initial.get(field_name)
                if initial is not None:
                    self.initial[field_name] = [unicode(initial)]

    def clean(self):
        cleaned_data = super(DreamSuitePaperForm, self).clean()

        for field_name in cleaned_data.keys():
            field = self.fields[field_name]
            if (
                isinstance(field.widget, forms.CheckboxSelectMultiple) and
                field.choices == BOOLEAN_CHOICES
                or
                field_name == 'victim_was_hidden' or
                field_name == 'victim_was_free_to_go_out'
            ):
                if len(cleaned_data[field_name]) > 0:
                    value = cleaned_data[field_name][0]
                    if value == "True":
                        cleaned_data[field_name] = True
                    elif value == "False":
                        cleaned_data[field_name] = False
                    else:
                        cleaned_data[field_name] = None
                else:
                    cleaned_data[field_name] = None

        return cleaned_data

    def at_least_one_checked(self, cleaned_data, field_name_start):
        for field_name in cleaned_data.keys():
            if field_name.startswith(field_name_start):
                if isinstance(self.fields[field_name].widget, forms.CheckboxInput):
                    if cleaned_data[field_name]:
                        return True
        return False


class InterceptionRecordForm(DreamSuitePaperForm):
    contact_paid = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    name_came_up_before = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    ignore_warnings = forms.BooleanField(
        required=False
    )

    irf_number = FormNumberField(max_length=20)

    class Meta:
        model = InterceptionRecord
        exclude = [ 'form_entered_by', 'date_form_received' ]


    def __init__(self, *args, **kwargs):
        super(InterceptionRecordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.iteritems():
            if type(field) == forms.fields.BooleanField:
                try:
                    model_field = InterceptionRecord._meta.get_field_by_name(field_name)[0]
                    if hasattr(model_field, 'weight'):
                        field.weight = model_field.weight
                except:
                    pass  # Don't worry about this for non-model fields like ignore_warnings

    def clean(self):
        cleaned_data = super(InterceptionRecordForm, self).clean()
        self.has_warnings = False

        self.ensure_at_least_one_interceptee(cleaned_data)
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
        self.get_pictures(cleaned_data)
        return cleaned_data

    def get_pictures(self, cleaned_data):
        pass

    def ensure_at_least_one_interceptee(self, cleaned_data):
        if len([
            (key, value) for key, value in self.data.items()
                if key.startswith('interceptees') and key.endswith('name') and value != u''
        ]) == 0:
            self._errors['interceptees'] = self.error_class(['At least one interceptee must be listed.'])

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
            self._errors['first_page_area'] = self.error_class(['At least one box must be checked on the first page.'])

    def box_six_or_seven_must_be_checked(self, cleaned_data):
        if not (
                cleaned_data.get('contact_noticed') or
                cleaned_data.get('staff_noticed')
        ):
            self._errors['contact_noticed'] = self.error_class(['Either Contact (6.0) or Staff (7.0) must be chosen for how interception was made.'])

    def if_box_six_checked_at_least_one_from_six_one_to_six_nine_must_be_checked(self, cleaned_data):
        if cleaned_data.get('contact_noticed') and not (
            cleaned_data.get('which_contact_hotel_owner') or
            cleaned_data.get('which_contact_rickshaw_driver') or
            cleaned_data.get('which_contact_taxi_driver') or
            cleaned_data.get('which_contact_bus_driver') or
            cleaned_data.get('which_contact_church_member') or
            cleaned_data.get('which_contact_other_ngo') or
            cleaned_data.get('which_contact_police') or
            cleaned_data.get('which_contact_subcommittee_member') or
            cleaned_data.get('which_contact_other')
        ):
            self._errors['contact_noticed'] = self.error_class(
                ['Contact (6.0) chosen for how interception was made, but a specific kind was not specified (6.1-6.9).'])

    def if_box_six_other_is_checked_the_other_value_must_be_present(self, cleaned_data):
        if cleaned_data.get('which_contact_other') and not cleaned_data.get('which_contact_other_value'):
            self._errors['which_contact_other_value'] = self.error_class(
                ['Other chosen for Contact but the kind is not specified.'])

    def if_contact_noticed_ensure_contact_paid(self, cleaned_data):
        if cleaned_data.get('contact_noticed') and cleaned_data.get('contact_paid') == []:
            self._errors['contact_paid'] = self.error_class(
                ['Contact noticed chosen but paid not specified.'])

    def if_8_2_ensure_number_specified(self, cleaned_data):
        if cleaned_data.get('call_thn_to_cross_check') and cleaned_data.get('name_came_up_before') == []:
            self._errors['name_came_up_before'] = self.error_class(
                ['This field is required.'])
        if cleaned_data.get('call_thn_to_cross_check') and cleaned_data.get('name_came_up_before') and not cleaned_data.get('name_came_up_before_value'):
            self._errors['name_came_up_before'] = self.error_class(
                ['A number must be given.'])

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
            self._errors['red_flags'] = error

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
        if not (cleaned_data.get('interception_type_gulf_countries') or
                cleaned_data.get('interception_type_india_trafficking') or
                cleaned_data.get('interception_type_unsafe_migration') or
                cleaned_data.get('interception_type_circus') or
                cleaned_data.get('interception_type_runaway')):
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


class IntercepteeForm(DreamSuitePaperForm):
    class Meta:
        model = Interceptee
        exclude = ('district','vdc')

    def __init__(self, *args, **kwargs):
        super(IntercepteeForm, self).__init__(*args, **kwargs)
        self.fields['district'] = DistrictField(required=False)
        self.fields['vdc'] = VDCField(required=False)
        try:
            self.fields['district'].initial = self.instance.district
        except:
            pass
        try:
           self.fields['vdc'].initial = self.instance.vdc
        except:
            pass

    def save(self, commit=True):
        try:
            district = District.objects.get(name=self.cleaned_data['district'])
            self.instance.district = district
        except District.DoesNotExist:
            pass

        try:
            vdc = VDC.objects.get(name=self.cleaned_data['vdc'])
            self.instance.vdc = vdc
        except VDC.DoesNotExist:
            pass

        return super(IntercepteeForm, self).save(commit)

IntercepteeFormSet = inlineformset_factory(InterceptionRecord, Interceptee, exclude=[], extra=12)

class VictimInterviewForm(DreamSuitePaperForm):
    statement_read_before_beginning = forms.BooleanField(
        required=True,
        error_messages={'invalid_choice': 'This box must be checked.'}
    )

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

    victim_had_suicidal_thoughts = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    other_people_and_places_involved = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    ignore_warnings = forms.BooleanField(
        required=False
    )

    has_signature = forms.BooleanField(
        required=True,
        error_messages={'invalid_choice': 'This box must be checked.'}
    )

    vif_number = FormNumberField(max_length=20)

    victim_where_going_region_india = forms.BooleanField(label='India', required=False)
    victim_where_going_region_gulf = forms.BooleanField(label='Gulf / Other', required=False)

    victim_where_going_india_delhi = forms.BooleanField(label='Delhi', required=False)
    victim_where_going_india_mumbai = forms.BooleanField(label='Mumbai', required=False)
    victim_where_going_india_surat = forms.BooleanField(label='Surat', required=False)
    victim_where_going_india_rajastan = forms.BooleanField(label='Rajastan', required=False)
    victim_where_going_india_kolkata = forms.BooleanField(label='Kolkata', required=False)
    victim_where_going_india_pune = forms.BooleanField(label='Pune', required=False)
    victim_where_going_india_jaipur = forms.BooleanField(label='Jaipur', required=False)
    victim_where_going_india_bihar = forms.BooleanField(label='Bihar', required=False)
    victim_where_going_india_didnt_know = forms.BooleanField(label='Did Not Know', required=False)
    victim_where_going_india_other = forms.BooleanField(label='Other', required=False)

    victim_where_going_gulf_lebanon = forms.BooleanField(label='Lebanon', required=False)
    victim_where_going_gulf_dubai = forms.BooleanField(label='Dubai', required=False)
    victim_where_going_gulf_malaysia = forms.BooleanField(label='Malaysia', required=False)
    victim_where_going_gulf_oman = forms.BooleanField(label='Oman', required=False)
    victim_where_going_gulf_saudi_arabia = forms.BooleanField(label='Saudi Arabia', required=False)
    victim_where_going_gulf_kuwait = forms.BooleanField(label='Kuwait', required=False)
    victim_where_going_gulf_qatar = forms.BooleanField(label='Qatar', required=False)
    victim_where_going_gulf_didnt_know = forms.BooleanField(label='Did Not Know', required=False)
    victim_where_going_gulf_other = forms.BooleanField(label='Other', required=False)

    victim_address_district = DistrictField(label='District')
    victim_address_vdc = VDCField(label='VDC')
    victim_guardian_address_district = DistrictField(label='District')
    victim_guardian_address_vdc = VDCField(label='VDC')

    class Meta:
        model = VictimInterview
        exclude = ('victim_address_district',
                   'victim_address_vdc',
                   'victim_guardian_address_district',
                   'victim_guardian_address_vdc')

    def __init__(self, *args, **kwargs):
        super(VictimInterviewForm, self).__init__(*args, **kwargs)

        # Determine the number of pbs and lbs. I can't come up with a better way than this
        self.num_pbs = 0
        self.num_lbs = 0
        for field_name, value in self.data.iteritems():
            if self.data[field_name]:
                if field_name.startswith('person_boxes-'):
                    try:
                        which = int(field_name.split('-')[1])
                        if which + 1 > self.num_pbs:
                            self.num_pbs = which + 1
                    except:
                        pass
                if field_name.startswith('location_boxes-'):
                    try:
                        which = int(field_name.split('-')[1])
                        if which + 1 > self.num_lbs:
                            self.num_lbs = which + 1
                    except:
                        pass
        self.box_pages_needed = max(
            1,
            (self.num_pbs - 1) / 3 + 1,
            (self.num_lbs - 1) / 2 + 1
        )
        try:
            self.fields['victim_address_district'].initial = self.instance.victim_address_district
        except:
            pass
        try:
            self.fields['victim_address_vdc'].initial = self.instance.victim_address_vdc
        except:
            pass
        try:
            self.fields['victim_guardian_address_district'].initial = self.instance.victim_guardian_address_district
        except:
            pass
        try:
            self.fields['victim_guardian_address_vdc'].initial = self.instance.victim_guardian_address_vdc
        except:
            pass

    def save(self, commit=True):
        victim_address_district = District.objects.get(name=self.cleaned_data['victim_address_district'])
        victim_address_vdc = VDC.objects.get(name=self.cleaned_data['victim_address_vdc'])
        victim_guardian_address_district = District.objects.get(name=self.cleaned_data['victim_guardian_address_district'])
        victim_guardian_address_vdc = VDC.objects.get(name=self.cleaned_data['victim_guardian_address_vdc'])
        self.instance.victim_address_district = victim_address_district
        self.instance.victim_address_vdc = victim_address_vdc
        self.instance.victim_guardian_address_district = victim_guardian_address_district
        self.instance.victim_guardian_address_vdc = victim_guardian_address_vdc
        return super(VictimInterviewForm, self).save(commit)


    def clean(self):
        cleaned_data = super(VictimInterviewForm, self).clean()
        self.has_warnings = False

        for field_name_start in [
            'primary_motivation',
            'migration_plans',
            'victim_primary_means_of_travel',
            'meeting_at_border',
            'awareness_before_interception',
            'attitude_towards_tiny_hands',
            'victim_heard_gospel',
            'legal_action_against_traffickers',
        ]:
            if not self.at_least_one_checked(cleaned_data, field_name_start):
                self._errors[field_name_start] = self.error_class(['This field is required.'])

        if not cleaned_data.get('ignore_warnings'):
            self.ensure_victim_where_going(cleaned_data)
            self.ensure_tiny_hands_rating(cleaned_data)

        return cleaned_data

    def ensure_victim_where_going(self, cleaned_data):
        if not self.at_least_one_checked(cleaned_data, 'victim_where_going'):
            error = self.error_class(['Field should be included, though not required.'])
            error.is_warning = True
            self.has_warnings = True
            self._errors['victim_where_going'] = error

    def ensure_tiny_hands_rating(self, cleaned_data):
        for field_name in [
                'tiny_hands_rating_border_staff',
                'tiny_hands_rating_shelter_staff',
                'tiny_hands_rating_trafficking_awareness',
                'tiny_hands_rating_shelter_accommodations']:
            if not cleaned_data.get(field_name):
                error = self.error_class(['Field should be included, though not required.'])
                error.is_warning = True
                self.has_warnings = True
                self._errors[field_name] = error


class VictimInterviewPersonBoxForm(DreamSuitePaperForm):

    gender = forms.MultipleChoiceField(
        choices=VictimInterviewPersonBox.GENDER_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    associated_with_place = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = VictimInterviewPersonBox
        exclude = ('address_district', 'address_vdc')

    def __init__(self, *args, **kwargs):
        super(VictimInterviewPersonBoxForm, self).__init__(*args, **kwargs)
        initial = self.initial.get('gender')
        if initial is not None:
            self.initial['gender'] = [unicode(initial)]
        self.fields['address_district'] = DistrictField(label="District")
        self.fields['address_vdc'] = VDCField(label="VDC")
        try:
            self.fields['address_district'].initial = self.instance.address_district
        except:
            pass
        try:
           self.fields['address_vdc'].initial = self.instance.address_vdc
        except:
            pass

    def save(self, commit=True):
        address_district = District.objects.get(name=self.cleaned_data['address_district'])
        address_vdc = VDC.objects.get(name=self.cleaned_data['address_vdc'])
        self.instance.address_vdc = address_vdc
        self.instance.address_district = address_district
        return super(VictimInterviewPersonBoxForm, self).save(commit)

    def clean(self):
        cleaned_data = super(VictimInterviewPersonBoxForm, self).clean()
        if len(cleaned_data.get('gender', [])) > 0:
            cleaned_data['gender'] = cleaned_data['gender'][0]
        else:
            cleaned_data['gender'] = ''

        return cleaned_data


class VictimInterviewLocationBoxForm(DreamSuitePaperForm):
    associated_with_person = forms.MultipleChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = VictimInterviewLocationBox
        exclude = ('district','vdc')

    def __init__(self, *args, **kwargs):
        super(VictimInterviewLocationBoxForm, self).__init__(*args, **kwargs)
        self.fields['district'] = DistrictField(label="District")
        self.fields['vdc'] = VDCField(label="VDC")
        try:
            self.fields['district'].initial = self.instance.district
        except:
            pass
        try:
           self.fields['vdc'].initial = self.instance.vdc
        except:
            pass

    def save(self, commit=True):
        district = District.objects.get(name=self.cleaned_data['district'])
        vdc = VDC.objects.get(name=self.cleaned_data['vdc'])
        self.instance.vdc = vdc
        self.instance.district = district
        return super(VictimInterviewLocationBoxForm, self).save(commit)

class BorderStationForm(forms.ModelForm):
    class Meta:
        model = BorderStation
        fields = '__all__'
        widgets = {
            'date_established': forms.TextInput(attrs={'placeholder': '12/31/12'}),
        }

    def clean_station_code(self):
        return self.cleaned_data['station_code'].upper()


class VDCForm(forms.ModelForm):
    class Meta:
        model = VDC
        fields = ['name','latitude','longitude','cannonical_name','district','verified']
