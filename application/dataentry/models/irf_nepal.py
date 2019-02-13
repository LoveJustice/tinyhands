from django.db import models
from .irf_core import IrfCore, IntercepteeCore

class IrfNepal(IrfCore):
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    seen_in_last_month_in_nepal = models.BooleanField("Meeting someone she's seen in Nepal in the last month", default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    group_missed_call = models.BooleanField('Missed Call', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    who_in_group_engaged = models.BooleanField('Fiancée', default=False)
    who_in_group_dating = models.BooleanField('Boyfriend / Girlfriend', default=False)
    relationship_to_get_married = models.BooleanField('Coming to get married', default=False)
    wife_under_18 = models.BooleanField('Wife is under 18', default=False)
    less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False)
    between_2_12_weeks_before_eloping = models.BooleanField('2-12 weeks before eloping', default=False)
    caste_not_same_as_relative = models.BooleanField('Caste not the same as alleged relative', default=False)
    contradiction_between_stories = models.BooleanField('Contradiction between stories', default=False)

    doesnt_know_going_to_india = models.BooleanField("Doesn't know she's going to India", default=False)
    where_going_someone_paid_expenses = models.BooleanField('Non relatives paid for their travel', default=False)
    where_going_visit = models.BooleanField('Visit / Family / Returning Home', default=False)
    where_going_shopping = models.BooleanField('Shopping', default=False)
    where_going_treatment = models.BooleanField('Treatment', default=False)
    
    no_address_at_destination = models.BooleanField('No address at destination', default=False)
    no_company_phone = models.BooleanField('No company phone number', default=False)
    no_appointment_letter = models.BooleanField('No Appointment Letter', default=False)
    valid_gulf_country_visa = models.BooleanField('Has a valid gulf country visa in passport', default=False)
    going_to_gulf_through_india = models.BooleanField('Going to Gulf for work through India', default=False)
    
    no_bags_long_trip = models.BooleanField('No bags though claim to be going for a long time', default=False)
    shopping_overnight_stuff_in_bags = models.BooleanField('Shopping - Stuff for overnight stay in bags', default=False)
    
    reluctant_treatment_info = models.BooleanField('Reluctant to give info about treatment', default=False)
    no_medical_documents = models.BooleanField('Does not have medical documents', default=False)
    fake_medical_documents = models.BooleanField('Fake Medical documents', default=False)
    no_medical_appointment = models.BooleanField('No medical appointment', default=False)
    
    doesnt_know_villiage_details = models.BooleanField("Doesn't know details about village", default=False)
    reluctant_villiage_info = models.BooleanField('Reluctant to give info about village', default=False)
    
    family_doesnt_know_where_going_18_23 = models.BooleanField('18-23 Family doesnt know where they are going', default=False)
    family_unwilling_to_let_go_18_23 = models.BooleanField('18-23 Family unwilling to let them go', default=False)
    over_23_family_unwilling_to_let_go = models.BooleanField('Over 23 Family unwilling to let them go', default=False)

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
    noticed_walking_to_border = models.BooleanField('Walking to border', default=False)
    noticed_roaming_around = models.BooleanField('Roaming around', default=False)
    noticed_exiting_vehicle = models.BooleanField('Exiting vehicle', default=False)
    noticed_heading_to_vehicle = models.BooleanField('Heading to vehicle', default=False)
    noticed_in_a_vehicle = models.BooleanField('In a vehicle', default=False)
    noticed_in_a_rickshaw = models.BooleanField('In a rickshaw', default=False)
    noticed_in_a_cart = models.BooleanField('In a cart', default=False)
    noticed_carrying_a_baby = models.BooleanField('Carrying a baby', default=False)
    noticed_on_the_phone = models.BooleanField('On the phone', default=False)
    noticed_other_sign = models.CharField(max_length=127, blank=True)
    
    case_notes = models.TextField('Case Notes', blank=True)
    reason_for_intercept = models.TextField('Primary reason for intercept', blank=True)
    evidence_categorization = models.CharField(max_length=127, null=True)
    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms', default='', blank=True)
    
class IntercepteeNepal(IntercepteeCore):
    interception_record = models.ForeignKey(IrfNepal, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent