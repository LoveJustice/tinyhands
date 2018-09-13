from django.db import models
from .irf_core import IrfCore, IntercepteeCore

class IrfIndia(IrfCore):
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    seen_in_last_month_in_nepal = models.BooleanField("Meeting someone she's seen in Nepal in the last month", default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False)
    between_2_12_weeks_before_eloping = models.BooleanField('2-12 weeks before eloping', default=False)
    caste_not_same_as_relative = models.BooleanField('Caste not the same as alleged relative', default=False)
    group_missed_call = models.BooleanField('Missed Call', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    
    group_never_met_before = models.BooleanField("Meeting someone they haven't met before", default=False)
    group_wife_girl_nepali_bengali = models.BooleanField('Wife/girl is Nepali/Bengali', default=False)
    group_wife_girl_indian = models.BooleanField('Wife/girl is Indian under 18', default=False)
    
    where_going_visit = models.BooleanField('Visit / Family / Returning Home', default=False)
    where_going_shopping = models.BooleanField('Shopping', default=False)
    where_going_doesnt_know = models.BooleanField("Doesn't know where they are going", default=False)
    where_going_someone_paid_expenses = models.BooleanField('Someone (not a relative) paid their travel expenses', default=False)
    where_going_dont_know_what_doing = models.BooleanField("Don't know the details of what they will be doing", default=False)
    where_going_running_from_india = models.BooleanField('Running away from India (under 18)', default=False)
    where_going_enticed = models.BooleanField('Someone enticed them to leave', default=False)
    
    no_address_at_destination = models.BooleanField('No address at destination', default=False)
    no_company_phone = models.BooleanField('No company phone number', default=False)
    no_appointment_letter = models.BooleanField('No Appointment Letter', default=False)
    valid_gulf_country_visa = models.BooleanField('Has a valid gulf country visa in passport', default=False)
    going_to_gulf_through_india = models.BooleanField('Going to Gulf for work through India', default=False)
    
    no_bags_long_trip = models.BooleanField('No bags though claim to be going for a long time', default=False)
    shopping_overnight_stuff_in_bags = models.BooleanField('Shopping - Stuff for overnight stay in bags', default=False)
    
    over_18_family_doesnt_know = models.BooleanField('Family members do not know they is going to India', default=False)
    over_18_family_unwilling = models.BooleanField('Family members unwilling to let them go', default=False)
    
    which_contact = models.CharField(max_length=127, blank=True)
    contact_paid = models.NullBooleanField(null=True)
    contact_paid_how_much = models.CharField('How much?', max_length=255, blank=True)
    
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
    noticed_foreign_looking = models.BooleanField('Indian looking', default=False)
    noticed_typical_village_look = models.BooleanField('Typical village look', default=False)
    noticed_looked_like_agent = models.BooleanField('Looked like agent', default=False)
    noticed_caste_difference = models.BooleanField('Caste difference', default=False)
    noticed_young_looking = models.BooleanField('Young looking', default=False)

    # Action
    noticed_waiting_sitting = models.BooleanField('Waiting / sitting', default=False)
    noticed_on_train = models.BooleanField('on train', default=False)
    noticed_roaming_around = models.BooleanField('Roaming around', default=False)
    noticed_exiting_vehicle = models.BooleanField('Exiting vehicle', default=False)
    noticed_heading_to_vehicle = models.BooleanField('Heading to vehicle', default=False)
    noticed_in_a_vehicle = models.BooleanField('In a vehicle', default=False)
    noticed_in_a_rickshaw = models.BooleanField('In a rickshaw', default=False)
    noticed_in_a_cart = models.BooleanField('In a cart', default=False)
    noticed_carrying_a_baby = models.BooleanField('Carrying a baby', default=False)
    noticed_on_the_phone = models.BooleanField('On the phone', default=False)
    noticed_other_sign = models.CharField(max_length=127, blank=True)
    
    call_subcommittee = models.BooleanField('Call Subcommittee Chairperson/Vice-Chairperson/Secretary', default=False)
    call_project_manager = models.BooleanField('Call Project Manager to confirm intercept', default=False)
    
    reason_for_intercept = models.TextField('Reason For Intercept', blank=True)
    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms', default='', blank=True)
    
class IntercepteeIndia(IntercepteeCore):
    interception_record = models.ForeignKey(IrfIndia, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent