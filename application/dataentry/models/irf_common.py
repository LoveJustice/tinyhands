from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .person import Person
from .form import BaseCard
from .form import BaseForm

# Class to store an instance of the IRF data.
# This should contain data that is common for all IRFs and is not expected to be changed
class IrfCommon(BaseForm):
    # Top Box
    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    location = models.CharField('Location:', max_length=255)
    date_of_interception = models.DateField('Interception date', null=True, default=None)
    time_of_interception = models.TimeField(null=True)
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)
    staff_name = models.CharField('Staff Name:', max_length=255)
    
    #Profile
    profile = models.CharField(max_length=1024, blank=True)
    
    #area/Industry
    industry = models.CharField('Industry', max_length=1024, blank=True)
    where_going_destination = models.CharField('Location:', max_length=1024, blank=True)
    
    #Resources/Safety
    vulnerability_afraid_of_host = models.BooleanField('Afraid of host/employer/recruiter', default=False)
    vulnerability_doesnt_speak_destination_language = models.BooleanField("Doesn't speak language of destination", default=False)
    vulnerability_group_facebook = models.BooleanField('Facebook', default=False)
    vulnerability_group_missed_call = models.BooleanField('Missed Call', default=False)
    vulnerability_group_never_met_before = models.BooleanField('Meeting someone for the first time', default=False)
    vulnerability_group_other_website = models.CharField(max_length=127, blank=True)
    vulnerability_met_on_the_way = models.BooleanField('Met on their way', default=False)
    vulnerability_person_speaking_on_their_behalf = models.BooleanField('Person is not speaking on their own behalf / someone is speaking for them', default=False)
    vulnerability_refuses_family_info = models.BooleanField('Will not give family info', default=False).set_weight(35)
    vulnerability_supporting_documents_one_way_ticket = models.BooleanField('One way ticket', default=False)
    vulnerability_under_18_family_doesnt_know = models.BooleanField("Family doesn't know she is going to India", default=False).set_weight(45)
    vulnerability_insufficient_resource = models.BooleanField('insufficient resources_to live/get home', default=False)
    vulnerability_minor_without_guardian = models.BooleanField('Minor unaccompanied by guardian', default=False)
    vulnerability_family_unwilling = models.BooleanField('Family unwilling to let them go', default=False)
    vulnerability_first_time_traveling_abroad = models.BooleanField('First time traveling abroad', default=False)
    vulnerability_doesnt_speak_english = models.BooleanField("Doesn't speak English", default=False)
    vulnerability_non_relative_paid_flight = models.BooleanField('Non-relative paid for flight', default=False)
    vulnerability_paid_flight_in_cash = models.BooleanField('Non-relative paid for flight', default=False)
    vulnerability_connection_host_unclear = models.BooleanField('Connection to host/suspect limited or unclear', default=False)
    vulnerability_doesnt_have_required_visa = models.BooleanField("Doesn't have required visa/docs", default=False)
    vulnerability_family_friend_arranged_travel = models.BooleanField("Friend/Family arranged travel/job/studies", default=False)
    vulnerability_where_going_doesnt_know = models.BooleanField("Doesn't know where they are going", default=False)
    
    vulnerability_no_id = models.BooleanField("Does not have any form of ID", default=False)
    vulnerability_bus_driver_payment_at_destination = models.BooleanField("Bus driver expecting payment for travel at destination", default=False)
    vulnerability_first_time_traveling_to_city = models.BooleanField("Travelling to city from rural area for first time", default=False)
    vulnerability_no_mobile_phone = models.BooleanField("Does not own mobile phone", default=False)
    
    evade_appearance_avoid_officials = models.BooleanField('Avoiding officials/hesitant to talk', default=False)
    evade_caught_in_lie = models.BooleanField('Caught in a lie or contradiction', default=False).set_weight(35)
    evade_couldnt_confirm_job = models.BooleanField('Could not confirm job', default=False).set_weight(10)
    evade_job_details_changed_en_route = models.BooleanField('Job details were changed en route', default=False)
    evade_no_bags_long_trip = models.BooleanField('No bags though claim to be going for a long time', default=False)
    evade_noticed_carrying_full_bags = models.BooleanField('Carrying Full bags', default=False)
    evade_signs_confirmed_deception = models.BooleanField('Called place and confirmed deception', default=False)
    evade_signs_fake_documentation = models.BooleanField('Fake documents', default=False)
    evade_signs_forged_false_documentation = models.BooleanField('Forged or falsified documents', default=False)
    evade_signs_other = models.CharField(max_length=127, blank=True)
    evade_signs_treatment = models.BooleanField('Treatment - no documentation / knowledge', default=False)
    evade_study_doesnt_know_school_details = models.BooleanField('Does not know details of school', default=False)
    evade_visa_misuse = models.BooleanField('Misuse - for purposes other than issued', default=False)
    
    #Control
    control_led_other_country = models.BooleanField('Led to other country without their knowledge', default=False)
    control_traveling_because_of_threat = models.BooleanField('Traveling because of a threat', default=False)
    control_owes_debt = models.BooleanField('Owes debt to person who recruited/paid travel', default=False)
    control_job = models.CharField(max_length=127, blank=True)
    control_promised_pay = models.CharField(max_length=127, blank=True)
    control_normal_pay = models.CharField(max_length=127, blank=True)
    control_promised_double = models.BooleanField('Promised pay more than double normal pay', default=False)
    control_promised_higher = models.BooleanField('Promised pay a little higher than normal pay', default=False)
    control_no_address_phone = models.BooleanField('No address / phone number (of job)', default=False)
    control_contradiction_stories = models.BooleanField('Contradiction between stories', default=False)
    control_drugged_or_drowsy = models.BooleanField('Girl appears drugged or drowsy', default=False)
    control_job_underqualified = models.BooleanField('Extremely underqualified for job', default=False)
    control_less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False)
    control_married_in_past_2_8_weeks = models.BooleanField('Married within the past 2-8 weeks', default=False).set_weight(10)
    control_married_in_past_2_weeks = models.BooleanField('Married in the past 2 weeks', default=False).set_weight(15)
    control_mobile_phone_taken_away = models.BooleanField('Their mobile phone was taken away', default=False)
    control_abducted = models.BooleanField('Abducted', default=False)
    control_not_real_job = models.BooleanField('Not a real job', default=False).set_weight(55)
    control_passport_with_broker = models.BooleanField('Passport is with a broker', default=False).set_weight(40)
    control_relationship_to_get_married = models.BooleanField('On their way to get married ', default=False)
    control_reported_total_red_flags = models.IntegerField('Reported Total Red Flag Points:', null=True, blank=True)
    control_status_known_trafficker = models.BooleanField('Is a known trafficker', default=False)
    control_connected_known_trafficker = models.BooleanField('Is connected to a known trafficker', default=False)
    control_traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    control_under_18_family_unwilling = models.BooleanField('Family unwilling to let her go', default=False).set_weight(60)
    control_where_going_someone_paid_expenses = models.BooleanField('Non relatives paid for their travel', default=False)
    control_wife_under_18 = models.BooleanField("Wife/fiancee is under 18", default=False)
    
    #Contact/Staff
    case_notes = models.TextField('Case Notes', blank=True)
    contact_paid = models.NullBooleanField(null=True)
    contact_paid_how_much = models.CharField('How much?', max_length=255, blank=True)
    rescue = models.BooleanField('Rescue', default=False)
    staff_who_noticed = models.CharField('Staff who noticed:', max_length=255, blank=True)
    talked_to_family_member = models.CharField(max_length=127, blank=True)
    which_contact = models.CharField(max_length=127, blank=True)
    who_noticed = models.CharField(max_length=127, null=True)
    
    #Reason
    call_subcommittee = models.BooleanField('Call Subcommittee Chairperson/Vice-Chairperson/Secretary', default=False)
    call_project_manager = models.BooleanField('Call Project Manager to confirm intercept', default=False)
    computed_total_red_flags = models.IntegerField('Computed Total Red Flag Points:', null=True, blank=True)
    convinced_by_staff = models.CharField(max_length=127, blank=True)
    convinced_by_family = models.CharField(max_length=127, blank=True)
    convinced_family_phone = models.CharField(max_length=127, blank=True)
    convinced_by_police = models.CharField(max_length=127, blank=True)
    evidence_categorization = models.CharField(max_length=127, null=True)
    has_signature = models.BooleanField('Scanned form has signature?', default=False)
    HOW_SURE_TRAFFICKING_CHOICES = [
        (1, '1 - Not at all sure'),
        (2, '2 - Unsure but suspects it'),
        (3, '3 - Somewhat sure'),
        (4, '4 - Very sure'),
        (5, '5 - Absolutely sure'),
    ]
    how_sure_was_trafficking = models.IntegerField('How sure are you that it was trafficking case?', choices=HOW_SURE_TRAFFICKING_CHOICES, null=True)
    immigration_lj_entry = models.CharField(max_length=127, null=True)
    immigration_lj_transit = models.CharField(max_length=127, null=True)
    immigration_lj_exit = models.CharField(max_length=127, null=True)
    immigration_entry = models.CharField(max_length=127, null=True)
    immigration_transit = models.CharField(max_length=127, null=True)
    immigration_exit = models.CharField(max_length=127, null=True)
    immigration_case_number = models.CharField(max_length=127, null=True)
    reason_for_intercept = models.TextField('Primary reason for intercept', blank=True)
    flight_number = models.CharField(max_length=127, null=True)
    
    # Compliance
    logbook_received = models.DateField(null=True)
    logbook_incomplete_questions = models.CharField(max_length=127, blank=True)
    logbook_incomplete_sections = models.CharField(max_length=127, blank=True)
    logbook_information_complete = models.DateField(null=True)
    logbook_notes = models.TextField('Logbook Notes', blank=True)
    logbook_submitted = models.DateField(null=True)
    
    #Verification
    logbook_first_verification = models.CharField(max_length=127, blank=True)
    logbook_first_reason = models.TextField('First Reason', blank=True)
    logbook_followup_call = models.CharField(max_length=127, blank=True)
    logbook_first_verification_date = models.DateField(null=True)
    logbook_first_verification_name = models.CharField(max_length=127, blank=True)
    logbook_second_verification = models.CharField(max_length=127, blank=True)
    logbook_second_reason = models.TextField('Second Reason', blank=True)
    logbook_second_verification_date = models.DateField(null=True)
    logbook_second_verification_name = models.CharField(max_length=127, blank=True)
    
    logbook_champion_verification = models.BooleanField('Champion verification', default=False)
    
    def get_key(self):
        return self.irf_number
    
    def get_form_type_name(self):
        return 'IRF'
    
    def get_form_date(self):
        return self.date_of_interception
    
    def to_str(self, value):
        if value is None:
            return 'None'
        else:
            return str(value)
    
    def __str__(self):
        return self.to_str(self.id) + ":" + self.to_str(self.irf_number) + ", " + self.to_str(self.number_of_victims) + ", " + self.to_str(self.location )+ ", " + self.to_str(self.number_of_traffickers) + ", " + self.to_str(self.staff_name)
    
    @staticmethod
    def key_field_name():
        return 'irf_number'
    
    class Meta:
        indexes = [
            models.Index(fields=['logbook_submitted', 'station']),
            models.Index(fields=['logbook_first_verification_date', 'station']),
            models.Index(fields=['logbook_second_verification_date', 'station']),
        ]
    
class IntercepteeCommon(BaseCard):
    interception_record = models.ForeignKey(IrfCommon, related_name='interceptees', on_delete=models.CASCADE)
    relation_to = models.CharField(max_length=255, blank=True)
    person = models.ForeignKey(Person, null=True, blank=True)
    not_physically_present = models.BooleanField('Not physically present', default=False)
    consent_to_use_photo = models.CharField(max_length=255, null=True)
    consent_to_use_information = models.CharField(max_length=255, null=True)

    def address1_as_string(self):
        rtn = ''
        try:
            rtn = self.person.address1
        except Exception:
            pass
        
        return rtn

    def address2_as_string(self):
        rtn = ''
        try:
            rtn = self.person.address2
        except Exception:
            pass
        
        return rtn
    
    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent

class IrfAttachmentCommon(BaseCard):
    interception_record = models.ForeignKey(IrfCommon)
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms')
    private_card = models.BooleanField(default=True)
    option = models.CharField(max_length=126, null=True)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent
        
    def is_private(self):
        return self.private_card
    