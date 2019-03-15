from django.db import models
from .irf_core import IrfCore, IntercepteeCore, IrfAttachment

class IrfSouthAfrica(IrfCore):
    # Visual Section
    appearance_drug_withdrawl = models.BooleanField('Signs of Drug withdrawl', default=False)
    appearance_abuse = models.BooleanField('Signs of Abuse', default=False)
    appearance_disorientated = models.BooleanField('Disorientated/Uncertain', default=False)
    appearance_impoverished = models.BooleanField('Impoverished', default=False)
    appearance_long_jouney_little_luggage = models.BooleanField('Long journey but little luggage', default=False)
    appearance_revealing_clothing = models.BooleanField('Revealing clothing', default=False)
    appearance_avoid_officials = models.BooleanField('Avoiding officials/hesitant to talk', default=False)
    appearance_group_doesnt_know = models.BooleanField('Group that does not know each other', default=False)
    appearance_with_chaperone = models.BooleanField('With a chaperone', default=False)
    
    # Documentation Section
    passport_imposter = models.BooleanField('Imposter', default=False)
    passport_fraudulent = models.BooleanField('Fake', default=False)
    passport_illegally_obtained = models.BooleanField('Illegally obtained', default=False)
    passport_expired = models.BooleanField('Expired', default=False)
    
    visa_none = models.BooleanField('None', default=False)
    visa_fake = models.BooleanField('Fake', default=False)
    visa_misuse = models.BooleanField('Misuse - for purposes other than issued', default=False)
    visa_doesnt_match_nature = models.BooleanField('Nature of travel', default=False)
    visa_doesnt_match_duration = models.BooleanField('Duration of travel', default=False)
    visa_doesnt_match_destination = models.BooleanField('Destination of travel', default=False)
    
    supporting_documents_none = models.BooleanField('None', default=False)
    supporting_documents_fraudulent = models.BooleanField('Fake', default=False)
    supporting_documents_insufficient = models.BooleanField('Insufficient', default=False)
    supporting_documents_inaccurate = models.BooleanField('Inaccurate', default=False)
    supporting_documents_one_way_ticket = models.BooleanField('One way ticket', default=False)
    
    destination_middle_east = models.BooleanField('Middle east', default=False)
    destination_lesotho = models.BooleanField('Lesotho', default=False)
    destination_mozambique = models.BooleanField('Mozambique', default=False)
    destination_nigeria = models.BooleanField('Nigeria', default=False)
    
    
    # Interview Section
    doesnt_speak_local_language = models.BooleanField('Does not speak English/local language', default=False)
    financial_support = models.BooleanField('Cannot support themselves financially', default=False)
    doesnt_know_travel_details = models.BooleanField('Does not know details of travel', default=False)
    no_return_ticket = models.BooleanField('No return ticket', default=False)
    in_debt_to_host = models.BooleanField('Is in debt to host/employer/recruiter', default=False)
    afraid_of_host = models.BooleanField('Afraid of host/employer/recruiter', default=False)
    being_forced = models.BooleanField('Being forced', default=False)
    host_non_relative_paid = models.BooleanField('Host/Recruiter is non-relative and paid for travel expenses', default=False)
    contradiction_in_story = models.BooleanField('contradicction in story', default=False)
    
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    employment_dance = models.BooleanField('Dance/modeling, domestic work, casino, bush lodge, conferences, soccer', default=False)
    employment_doesnt_exist = models.BooleanField('Place does not exist', default=False)
    employment_no_offer = models.BooleanField('No job offer', default=False)
    employment_unable_verify = models.BooleanField('Unable to verify', default=False)
    employment_employer_reluctant = models.BooleanField('Employer reluctant to give information to victim', default=False)
    
    visit_boyfriend = models.BooleanField('Visiting a boyfriend', default=False)
    visit_attend_event = models.BooleanField('Attending an event', default=False)
    visit_intend_work = models.BooleanField('Evidence of intention to work', default=False)
    visit_no_connection_to_host = models.BooleanField('No clear connection to host', default=False)
    visit_doesnt_know_host = models.BooleanField('Does not know host well', default=False)
    visit_unaware_who_fetching_them = models.BooleanField('Unaware of who is fetching them from airport', default=False)
    visit_no_itinerary = models.BooleanField('No travel itinerary', default=False)
    visit_abnormal_short_stay = models.BooleanField('Abnormally short stay', default=False)
    visit_unaware_who_fetch = models.BooleanField('Unaware of who is fetching them from airport', default=False) 
    
    relationship_social_media = models.BooleanField('Met on social media', default=False)
    relationship_married_two_months = models.BooleanField('Married in the past 2 months', default=False)
    relationship_suspect_forced_marriage = models.BooleanField('Suspect forced marriage', default=False)
    relationship_never_met = models.BooleanField('Never met in person', default=False)
    relationship_to_get_married = models.BooleanField('Coming to get married', default=False)
    relationship_dont_speak_same_language = models.BooleanField('Do not speak the same language', default=False)
    relationship_arranged_by_other = models.BooleanField('Arranged by someone else', default=False)
    
    study_school_doesnt_exist = models.BooleanField('School does not exist', default=False)
    study_doesnt_know_course_details = models.BooleanField('Does not know details of course', default=False)
    study_doesnt_know_school_details = models.BooleanField('Does not know details of school', default=False)
    study_doesnt_know_when_starts = models.BooleanField('Does not know when course starts', default=False)
    
    # Host Section
    story_caught_in_lie = models.BooleanField('Caught in lie', default=False)
    story_contradicts_pvot = models.BooleanField("Contradicts PVOT's story", default=False)
    story_claims_not_know = models.BooleanField('Claims not to know PVOT', default=False)
    story_invite_behalf_of_other = models.BooleanField('Inviting them on behalf of someone else', default=False)
    story_will_not_provide_permit = models.BooleanField('Hangs up when asked for permit/ID', default=False)
    story_illogical = models.BooleanField('Illogical story', default=False)
    story_bribe = models.BooleanField('Illogical story', default=False)
    
    paid_flight = models.BooleanField('Has paid for flight', default=False)
    paid_flight_cash = models.BooleanField('Flight was paid for in cash', default=False)
    paid_offer_expenses = models.BooleanField('Offering to pay without expectations/explanation', default=False)
    paid_no_payback_terms = models.BooleanField('Not determined payback terms', default=False)
    paid_for_accomodations = models.BooleanField('Paid for accomodations', default=False)
    
    status_not_legally_in_country = models.BooleanField('Not in country legally', default=False)
    status_known_trafficker = models.BooleanField('Is a know trafficker', default=False)
    status_trafficker_associated = models.BooleanField('Associated to known trafficker', default=False)
    status_illegal_activity = models.BooleanField('Involved in illegal activity', default=False)
    status_false_details = models.BooleanField('Provided false details', default=False)
    status_misuse_of_permit = models.BooleanField('Misuse of permit', default=False)
    
    #Green flags
    documentation_in_order = models.BooleanField('Documentation in order', default=False)
    no_red_flags = models.BooleanField('No red flags', default=False)
    story_consistent = models.BooleanField('Story consistent', default=False)
    details_validated_and_correted = models.BooleanField('Details were validated and corrected', default=False)
    
    # Children Section
    child_no_affidavit = models.BooleanField('No affidavit/birth certificate', default=False)
    child_fearful = models.BooleanField('Child fearful of handler', default=False)
    child_not_escorted = models.BooleanField('Not being escorted by direct relative', default=False)
    child_handler_inconsistent_story = models.BooleanField('Handler stories are inconsistent', default=False)
    child_handler_false_claims = models.BooleanField('Handler falsely claims to be relative', default=False)
    child_handler_criminal = models.BooleanField('Handler involved in criminal activity', default=False)
    
    child_relative_contacted  = models.CharField(max_length=127, default='', blank=True)

    # Source
    which_contact = models.CharField(max_length=127, default='', blank=True)
    name_of_contact = models.CharField(max_length=127, default='', blank=True)
    initial_signs = models.CharField(max_length=127, default='', blank=True)
    
    #Office Use Only
    entry_allowed = models.BooleanField('Entry allowed', default=False)
    entry_refused = models.BooleanField('Entry refused', default=False)
    transit_allowed = models.BooleanField('Transit allowed', default=False)
    transit_refused = models.BooleanField('Transit refused', default=False)
    believe_they_are_pvot = models.BooleanField('Do they believe they are PVOT?', default=False)
    require_assistance = models.BooleanField('Do they require assistance?', default=False)
    ims_case_number = models.CharField(max_length=127, default='', blank=True)
    case_report = models.BooleanField('Case report', default=False)
    cif = models.BooleanField('CIF', default=False)
    
    # Final Procedures
    interview_findings = models.CharField(max_length=127, null=True)
    case_notes = models.TextField('Case Notes', default='', blank=True)
    reason_believe_trafficked = models.TextField('What is the primary reason you believe this person is being trafficked or is at high risk of being trafficked', default='', blank=True)
    interception_made = models.CharField(max_length=127, null=True)
    handed_over_to =  models.CharField(max_length=127, default='', blank=True)



class IntercepteeSouthAfrica(IntercepteeCore):
    interception_record = models.ForeignKey(IrfSouthAfrica, related_name='interceptees', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent
        

class IrfAttachmentSouthAfrica(IrfAttachment):
    interception_record = models.ForeignKey(IrfSouthAfrica)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent