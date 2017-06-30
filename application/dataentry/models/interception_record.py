from django.db import models
from accounts.models import Account
from border_station import BorderStation


def set_weight(self, weight):
    self.weight = weight
    return self

models.BooleanField.set_weight = set_weight


class InterceptionRecord(models.Model):
    form_entered_by = models.ForeignKey(Account, related_name='irfs_entered', on_delete=models.CASCADE)
    date_form_received = models.DateTimeField()

    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    date_time_of_interception = models.DateTimeField('Date/Time:')

    date_time_entered_into_system = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)

    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)

    location = models.CharField('Location:', max_length=255)
    staff_name = models.CharField('Staff Name:', max_length=255)

    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_husbandwife = models.BooleanField('Husband / Wife', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)

    drugged_or_drowsy = models.BooleanField('Girl appears drugged or drowsy', default=False).set_weight(40)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False).set_weight(30)
    seen_in_last_month_in_nepal = models.BooleanField("Meeting someone she's seen in Nepal in the last month", default=False).set_weight(20)
    traveling_with_someone_not_with_her = models.BooleanField('Was travelling with someone not with her', default=False).set_weight(40)
    wife_under_18 = models.BooleanField('Wife is under 18', default=False).set_weight(45)
    married_in_past_2_weeks = models.BooleanField('Married in the past 2 weeks', default=False).set_weight(15)
    married_in_past_2_8_weeks = models.BooleanField('Married within the past 2-8 weeks', default=False).set_weight(10)
    less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False).set_weight(20)
    between_2_12_weeks_before_eloping = models.BooleanField('2-12 weeks before eloping', default=False).set_weight(15)
    caste_not_same_as_relative = models.BooleanField('Caste not the same as alleged relative', default=False).set_weight(50)
    caught_in_lie = models.BooleanField('Caught in a lie or contradiction', default=False).set_weight(35)
    other_red_flag = models.BooleanField('Other Red Flag', default=False).set_weight(0)
    other_red_flag_value = models.CharField(max_length=255, blank=True)

    # Where are you going, and for what?
    where_going_job = models.BooleanField('Job', default=False)
    where_going_visit = models.BooleanField('Visit / Family / Returning Home', default=False)
    where_going_shopping = models.BooleanField('Shopping', default=False)
    where_going_study = models.BooleanField('Study', default=False)
    where_going_treatment = models.BooleanField('Treatment', default=False)

    doesnt_know_going_to_india = models.BooleanField("Doesn't know she's going to India", default=False).set_weight(90)
    running_away_over_18 = models.BooleanField('Running away from home (18 years or older)', default=False).set_weight(20)
    running_away_under_18 = models.BooleanField('Running away from home (under 18 years old)', default=False).set_weight(50)
    going_to_gulf_for_work = models.BooleanField('Going to Gulf for work through India', default=False).set_weight(55)
    no_address_in_india = models.BooleanField('No address in India', default=False).set_weight(15)
    no_company_phone = models.BooleanField('No company phone number', default=False).set_weight(20)
    no_appointment_letter = models.BooleanField('No Appointment Letter', default=False).set_weight(10)
    valid_gulf_country_visa = models.BooleanField('Has a valid gulf country visa in passport', default=False).set_weight(35)
    passport_with_broker = models.BooleanField('Passport is with a broker', default=False).set_weight(40)
    job_too_good_to_be_true = models.BooleanField('Job is too good to be true', default=False).set_weight(40)

    not_real_job = models.BooleanField('Not a real job', default=False).set_weight(55)
    couldnt_confirm_job = models.BooleanField('Could not confirm job', default=False).set_weight(10)

    no_bags_long_trip = models.BooleanField('No bags though claim to be going for a long time', default=False).set_weight(20)

    shopping_overnight_stuff_in_bags = models.BooleanField('Shopping - Stuff for overnight stay in bags', default=False).set_weight(35)

    no_enrollment_docs = models.BooleanField('No documentation of enrollment', default=False).set_weight(15)
    doesnt_know_school_name = models.BooleanField("Does not Know School's Name and location", default=False).set_weight(40)
    no_school_phone = models.BooleanField('No phone number for School', default=False).set_weight(30)

    not_enrolled_in_school = models.BooleanField('Not enrolled in school', default=False).set_weight(60)

    reluctant_treatment_info = models.BooleanField('Reluctant to give info about treatment', default=False).set_weight(10)

    no_medical_documents = models.BooleanField('Does not have medical documents', default=False).set_weight(20)
    fake_medical_documents = models.BooleanField('Fake Medical documents', default=False).set_weight(70)

    no_medical_appointment = models.BooleanField('No medical appointment', default=False).set_weight(25)

    doesnt_know_villiage_details = models.BooleanField("Doesn't know details about village", default=False).set_weight(35)
    reluctant_villiage_info = models.BooleanField('Reluctant to give info about village', default=False).set_weight(15)
    reluctant_family_info = models.BooleanField('Reluctant to give family info', default=False).set_weight(10)
    refuses_family_info = models.BooleanField('Will not give family info', default=False).set_weight(35)

    under_18_cant_contact_family = models.BooleanField('No family contact established', default=False).set_weight(50)
    under_18_family_doesnt_know = models.BooleanField("Family doesn't know she is going to India", default=False).set_weight(45)
    under_18_family_unwilling = models.BooleanField('Family unwilling to let her go', default=False).set_weight(60)
    over_18_family_doesnt_know = models.BooleanField('Family members do not know she is going to India', default=False).set_weight(15)
    over_18_family_unwilling = models.BooleanField('Family members unwilling to let her go', default=False).set_weight(20)

    talked_to_family_member_brother = models.BooleanField('Own brother', default=False)
    talked_to_family_member_sister = models.BooleanField('Own sister', default=False)
    talked_to_family_member_father = models.BooleanField('Own father', default=False)
    talked_to_family_member_mother = models.BooleanField('Own mother', default=False)
    talked_to_family_member_grandparent = models.BooleanField('Own grandparent', default=False)
    talked_to_family_member_aunt_uncle = models.BooleanField('Own aunt / uncle', default=False)
    talked_to_family_member_other = models.BooleanField('Other', default=False)
    talked_to_family_member_other_value = models.CharField(max_length=255, blank=True)

    reported_total_red_flags = models.IntegerField('Reported Total Red Flag Points:', null=True, blank=True)

    # How did you make interception?
    contact_noticed = models.BooleanField('Contact', default=False)
    which_contact_hotel_owner = models.BooleanField('Hotel owner', default=False)
    which_contact_rickshaw_driver = models.BooleanField('Rickshaw driver', default=False)
    which_contact_taxi_driver = models.BooleanField('Taxi driver', default=False)
    which_contact_bus_driver = models.BooleanField('Bus driver', default=False)
    which_contact_church_member = models.BooleanField('Church member', default=False)
    which_contact_other_ngo = models.BooleanField('Other NGO', default=False)
    which_contact_police = models.BooleanField('Police', default=False)
    which_contact_subcommittee_member = models.BooleanField('Subcommittee member', default=False)
    which_contact_other = models.BooleanField('Other', default=False)
    which_contact_other_value = models.CharField(max_length=255, blank=True)

    # Did you pay this contact for the information?
    contact_paid = models.NullBooleanField(null=True)
    contact_paid_how_much = models.CharField('How much?', max_length=255, blank=True)

    staff_noticed = models.BooleanField('Staff', default=False)
    staff_who_noticed = models.CharField('Staff who noticed:', max_length=255, blank=True)

    # What was the sign that made you stop the girl for questioning? (check all that apply below)

    # Manner
    noticed_hesitant = models.BooleanField('Hesitant', default=False)
    noticed_nervous_or_afraid = models.BooleanField('Nervous or afraid', default=False)
    noticed_hurrying = models.BooleanField('Hurrying', default=False)
    noticed_drugged_or_drowsy = models.BooleanField('Drugged or drowsy', default=False)

    # Attire
    noticed_new_clothes = models.BooleanField('New clothes', default=False)
    noticed_dirty_clothes = models.BooleanField('Dirty clothes', default=False)
    noticed_carrying_full_bags = models.BooleanField('Carrying Full bags', default=False)
    noticed_village_dress = models.BooleanField('Village Dress', default=False)

    # Appearance
    noticed_indian_looking = models.BooleanField('Indian looking', default=False)
    noticed_typical_village_look = models.BooleanField('Typical village look', default=False)
    noticed_looked_like_agent = models.BooleanField('Looked like agent', default=False)
    noticed_caste_difference = models.BooleanField('Caste difference', default=False)
    noticed_young_looking = models.BooleanField('Young looking', default=False)

    # Action
    noticed_waiting_sitting = models.BooleanField('Waiting / sitting', default=False)
    noticed_walking_to_border = models.BooleanField('Walking to border', default=False)
    noticed_roaming_around = models.BooleanField('Roaming around', default=False)
    noticed_exiting_vehicle = models.BooleanField('Exiting vehicle', default=False)
    noticed_heading_to_vehicle = models.BooleanField('Heading to vehicle', default=False)
    noticed_in_a_vehicle = models.BooleanField('In a vehicle', default=False)
    noticed_in_a_rickshaw = models.BooleanField('In a rickshaw', default=False)
    noticed_in_a_cart = models.BooleanField('In a cart', default=False)
    noticed_carrying_a_baby = models.BooleanField('Carrying a baby', default=False)
    noticed_on_the_phone = models.BooleanField('On the phone', default=False)
    noticed_other_sign = models.BooleanField('Other sign:', default=False)
    noticed_other_sign_value = models.CharField(max_length=255, blank=True)

    # Procedures
    call_subcommittee_chair = models.BooleanField('Call Subcommittee Chair', default=False)
    call_thn_to_cross_check = models.BooleanField('Call THN to cross-check the names (6223856)', default=False)
    name_came_up_before = models.NullBooleanField(null=True)
    name_came_up_before_value = models.PositiveIntegerField('If yes, write the # from the table above:', null=True, blank=True)
    scan_and_submit_same_day = models.BooleanField('Scan and submit to THN the same day', default=False)

    interception_type_gulf_countries = models.BooleanField('Gulf Countries', default=False)
    interception_type_india_trafficking = models.BooleanField('India Trafficking', default=False)
    interception_type_unsafe_migration = models.BooleanField('Unsafe Migration', default=False)
    interception_type_circus = models.BooleanField('Circus', default=False)
    interception_type_runaway = models.BooleanField('Runaway', default=False)

    trafficker_taken_into_custody = models.CharField(max_length=20, null=True, blank=True)

    HOW_SURE_TRAFFICKING_CHOICES = [
        (1, '1 - Not at all sure'),
        (2, '2 - Unsure but suspects it'),
        (3, '3 - Somewhat sure'),
        (4, '4 - Very sure'),
        (5, '5 - Absolutely sure'),
    ]
    how_sure_was_trafficking = models.IntegerField(
        'How sure are you that it was trafficking case?',
        choices=HOW_SURE_TRAFFICKING_CHOICES)

    has_signature = models.BooleanField('Scanned form has signature?', default=False)

    case_notes = models.TextField('Case Notes', blank=True)

    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms', default='', blank=True)

    border_station = models.ForeignKey(BorderStation,  models.SET_NULL, null=True, blank=True)

    def calculate_total_red_flags(self):
        total = 0
        for field in self._meta.fields:
            if type(field) == models.BooleanField:
                value = getattr(self, field.name)
                if value is True:
                    if hasattr(field, 'weight'):
                        total += field.weight

        return total

    class Meta:
        ordering = ['-date_time_last_updated']
