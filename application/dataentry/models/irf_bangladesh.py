from django.db import models
from .irf_core import IrfAttachment, IrfCore, IntercepteeCore

class IrfBangladesh(IrfCore):
    # Group - Bangladesh specific
    group_missed_call = models.BooleanField('Missed Call', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    who_in_group_engaged = models.BooleanField('Engaged', default=False)
    who_in_group_dating = models.BooleanField('Dating Couple', default=False)

    group_never_met_before = models.BooleanField('Meeting someone for the first time', default=False)
    relationship_to_get_married = models.BooleanField('On their way to get married ', default=False)
    
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False)
    between_2_12_weeks_before_eloping = models.BooleanField('2-12 weeks before eloping', default=False)
    caste_not_same_as_relative = models.BooleanField('Caste not the same as alleged relative', default=False)
    waiting_likely_trafficker = models.BooleanField('Waiting for someone who fits description of trafficker', default=False)
    group_wife_girl_nepali_bengali = models.BooleanField('Wife/girl is Nepali/Bengali', default=False)
    contradiction_between_stories = models.BooleanField('Contradiction between stories', default=False)

    # Destination - Bangladesh specific
    where_going_border_area = models.BooleanField('Border Area', default=False)
    where_going_india = models.BooleanField('India', default=False)
    where_going_middle_east = models.BooleanField('Middle East', default=False)
    where_going_dont_know = models.BooleanField("Don't know", default=False)
    where_going_other = models.CharField("Other", max_length=127, blank=True)
    where_going_to_hotel = models.BooleanField('To Hotel', default=False)
    
    purpose_for_going_other = models.CharField("Other", max_length=127, blank=True)
    
    exploitative_situation = models.BooleanField('Escaping an exploitative situation', default=False)
    
    no_address_at_destination = models.BooleanField('No address at destination', default=False)
    no_company_phone = models.BooleanField('No company phone number', default=False)
    no_appointment_letter = models.BooleanField('No Appointment Letter', default=False)
    valid_gulf_country_visa = models.BooleanField('Has a valid gulf country visa in passport', default=False)
    known_place_bangladesh = models.CharField(max_length=127, blank=True)
    heading_for_border = models.BooleanField('Heading for a border area', default=False)
    dont_know_which_city = models.BooleanField("Don't know which town/city", default=False)
    traveling_through_india = models.BooleanField('Traveling through India', default=False)
    purpose_for_leaving_marriage = models.BooleanField('Marriage', default=False)
    dont_know_who_marry = models.BooleanField(" Doesn't know person they are going to marry", default=False)
    money_or_job_for_marriage = models.BooleanField('Was promised money or a job in exchange', default=False)
    unrealistic_benefit_for_marriage = models.BooleanField('Was promised unrealistic benefits for her family in exchange', default=False)
    
    # Family - Bangladesh specific
    doesnt_know_villiage_details = models.BooleanField("Doesn't know details about village", default=False)
    reluctant_villiage_info = models.BooleanField('Reluctant to give info about village', default=False)
    over_18_family_doesnt_know = models.BooleanField('Family members do not know they is going to India', default=False)
    over_18_family_unwilling = models.BooleanField('Family members unwilling to let them go', default=False)
    
    # Signs - Bangladesh specific
    which_contact = models.CharField(max_length=127, blank=True)
    contact_paid = models.NullBooleanField(null=True)
    contact_paid_how_much = models.CharField('How much?', max_length=255, blank=True)
    
    noticed_hesitant = models.BooleanField('Hesitant', default=False)
    noticed_nervous_or_afraid = models.BooleanField('Nervous or afraid', default=False)
    noticed_hurrying = models.BooleanField('Hurrying', default=False)

    noticed_new_clothes = models.BooleanField('New clothes', default=False)
    noticed_dirty_clothes = models.BooleanField('Dirty clothes', default=False)
    noticed_carrying_full_bags = models.BooleanField('Carrying Full bags', default=False)
    noticed_village_dress = models.BooleanField('Village Dress', default=False)

    noticed_foreign_looking = models.BooleanField('Indian looking', default=False)
    noticed_typical_village_look = models.BooleanField('Typical village look', default=False)
    noticed_looked_like_agent = models.BooleanField('Looked like agent', default=False)
    noticed_caste_difference = models.BooleanField('Caste difference', default=False)
    noticed_young_looking = models.BooleanField('Young looking', default=False)

    noticed_waiting_sitting = models.BooleanField('Waiting / sitting', default=False)
    noticed_roaming_around = models.BooleanField('Roaming around', default=False)
    noticed_exiting_vehicle = models.BooleanField('Exiting vehicle', default=False)
    noticed_heading_to_vehicle = models.BooleanField('Heading to vehicle', default=False)
    noticed_in_a_vehicle = models.BooleanField('In a vehicle', default=False)
    noticed_in_a_rickshaw = models.BooleanField('In a rickshaw', default=False)
    noticed_in_a_cart = models.BooleanField('In a cart', default=False)
    noticed_carrying_a_baby = models.BooleanField('Carrying a baby', default=False)
    noticed_on_the_phone = models.BooleanField('On the phone', default=False)
    noticed_walking_to_border = models.BooleanField('Walking to border', default=False)
    
     # Final Procedures - Bangladesh specific
    reason_for_intercept = models.TextField('Reason For Intercept', blank=True)
    case_notes = models.TextField('Case Notes', blank=True)
    interview_findings = models.CharField(max_length=127, blank=True)
    
class IntercepteeBangladesh(IntercepteeCore):
    interception_record = models.ForeignKey(IrfBangladesh, related_name='interceptees', on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent
        
class IrfAttachmentBangladesh(IrfAttachment):
    interception_record = models.ForeignKey(IrfBangladesh)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent