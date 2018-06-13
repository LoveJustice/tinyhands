from django.db import models
from .irf_core import IrfCore, IntercepteeCore

class IrfSouthAfrica(IrfCore):
    # Visual Section
    nationality_gender_asian_female = models.BooleanField('Asian Female', default=False)
    nationality_gender_pakistani_male = models.BooleanField('Pakistani Male', default=False)
    nationality_gender_bangladeshi_male = models.BooleanField('Bangladeshi Male', default=False)
    nationality_gender_nepali_male = models.BooleanField('Nepali Male', default=False)
    nationality_gender_african_female = models.BooleanField('African Female', default=False)
    nationality_gender_ethiopian_female = models.BooleanField('Ethipoian Female', default=False)
    nationality_gender_east_europe_female = models.BooleanField('Eastern Europe Female', default=False)
    nationality_gender_african_child = models.BooleanField('Any African child', default=False)
    nationality_gender_malawian_female = models.BooleanField('Malawian Female', default=False)
    nationality_gender_other = models.BooleanField('Other', default=False)
    
    appearance_drug_withdrawl = models.BooleanField('Signs of Drug withdrawl', default=False)
    appearance_abuse = models.BooleanField('Signs of Abuse', default=False)
    appearance_disorientated = models.BooleanField('Disorientated/Uncertain', default=False)
    appearance_impoverished = models.BooleanField('Impoverished', default=False)
    appearance_long_jouney_little_luggage = models.BooleanField('Long journey but little luggage', default=False)
    appearance_revealing_clothing = models.BooleanField('Revealing clothing', default=False)
    appearance_avoid_officials = models.BooleanField('Avoiding officials/hesitant to talk', default=False)
    appearance_lady_boy = models.BooleanField('Lady boy', default=False)
    appearance_group_doesnt_know = models.BooleanField('Group that does not know each other', default=False)
    appearance_with_chaperone = models.BooleanField('With a chaperone', default=False)
    
    # Documentation Section
    passport_imposter = models.BooleanField('Imposter', default=False)
    passport_fake = models.BooleanField('Fake', default=False)
    passport_illegally_obtained = models.BooleanField('Illegally obtained', default=False)
    passport_expired = models.BooleanField('Expired', default=False)
    
    visa_none = models.BooleanField('None', default=False)
    visa_fake = models.BooleanField('Fake', default=False)
    visa_misuse = models.BooleanField('Misuse - for purposes other than issued', default=False)
    visa_doesnt_match_nature = models.BooleanField('Nature of travel', default=False)
    visa_doesnt_match_duration = models.BooleanField('Duration of travel', default=False)
    visa_doesnt_match_destination = models.BooleanField('Destination of travel', default=False)
    
    supporting_documents_none = models.BooleanField('None', default=False)
    supporting_documents_fake = models.BooleanField('Fake', default=False)
    supporting_documents_insufficient = models.BooleanField('Insufficient', default=False)
    supporting_documents_inaccurate = models.BooleanField('Inaccurate', default=False)
    supporting_documents_one_way_ticket = models.BooleanField('One way ticket', default=False)
    
    destination_middle_east = models.BooleanField('Middle east', default=False)
    destination_ireland = models.BooleanField('Ireland', default=False)
    destination_manchester = models.BooleanField('Manchester', default=False)
    destination_swaziland = models.BooleanField('Swaziland', default=False)
    destination_mozambique = models.BooleanField('Mozambique', default=False)
    destination_nigeria = models.BooleanField('Nigeria', default=False)
    
    
    # Interview Section
    doesnt_speak_local_language = models.BooleanField('Does not speak English/local language', default=False)
    financial_support = models.BooleanField('Cannot support themselves financially', default=False)
    doesnt_know_travel_details = models.BooleanField('Does not know details of travel', default=False)
    in_debt_to_host = models.BooleanField('Is in debt to host/employer/recruiter', default=False)
    afraid_of_host = models.BooleanField('Afraid of host/employer/recruiter', default=False)
    being_forced = models.BooleanField('Being forced', default=False)
    
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    employment_dance = models.BooleanField('Dance/modeling, domestic work, casino, bush lodge, conferences, soccer', default=False)
    employment_doesnt_exist = models.BooleanField('Place does not exist', default=False)
    employment_no_offer = models.BooleanField('No job offer', default=False)
    employment_unable_verify = models.BooleanField('Unable to verify', default=False)
    employment_employer_reluctant = models.BooleanField('Employer reluctant to give information to victim', default=False)
    
    where_going_visit = models.BooleanField('Visit / Family / Returning Home', default=False)
    visit_boyfriend = models.BooleanField('Visiting a boyfriend', default=False)
    visit_attend_event = models.BooleanField('Attending an event', default=False)
    visit_intend_work = models.BooleanField('Evidence of intention to work', default=False)
    visit_doesnt_know_host = models.BooleanField('Does not know host well/No clear connection to host', default=False)
    visit_no_itinerary = models.BooleanField('No travel itinerary', default=False)
    visit_abnormal_short_stay = models.BooleanField('Abnormally short stay', default=False)  
    
    where_going_relationship = models.BooleanField('Relaionship', default=False)
    relationship_social_media = models.BooleanField('Met on social media', default=False)
    relationship_married_two_months = models.BooleanField('Married in the past 2 months', default=False)
    relationship_never_met = models.BooleanField('Never met in person', default=False)
    relationship_to_get_married = models.BooleanField('Coming to get married', default=False)
    relationship_dont_speak_same_language = models.BooleanField('Do not speak the same language', default=False)
    relationship_arranged_by_other = models.BooleanField('Arranged by someone else', default=False)
    
    study_school_doesnt_exist = models.BooleanField('School does not exist', default=False)
    study_doesnt_know_course_details = models.BooleanField('Does not know details of course', default=False)
    study_doesnt_know_school_details = models.BooleanField('Does not know details of school', default=False)
    study_doesnt_know_when_starts = models.BooleanField('Does not know when course starts', default=False)
    
    # Host Section
    story_claims_not_know = models.BooleanField('Claims not to know them', default=False)
    story_invite_behalf_of_other = models.BooleanField('Inviting them on behalf of someone else', default=False)
    story_illogical = models.BooleanField('Illogical story', default=False)
    story_bribe = models.BooleanField('Illogical story', default=False)
    
    paid_flight = models.BooleanField('Has paid for flight', default=False)
    paid_flight_cash = models.BooleanField('Flight was paid for in cash', default=False)
    paid_offer_expenses = models.BooleanField('Offering to pay all expenses without explanation', default=False)
    paid_no_payback_terms = models.BooleanField('No determined payback terms', default=False)
    
    status_not_legally_in_country = models.BooleanField('Not in country legally', default=False)
    status_known_trafficker = models.BooleanField('Is a know trafficker', default=False)
    status_trafficker_associated = models.BooleanField('Associated to known trafficker', default=False)
    status_illegal_activity = models.BooleanField('Involved in illegal activity', default=False)
    status_false_details = models.BooleanField('Provided false details', default=False)
    
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
    
    # Final Procedures
    case_notes = models.TextField('Case Notes', default='', blank=True)
    interception_made = models.CharField(max_length=127, null=True)
    handed_over_to =  models.CharField(max_length=127, default='', blank=True)
    
    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_irf_forms', default='', blank=True)



class IntercepteeSouthAfrica(IntercepteeCore):
    interception_record = models.ForeignKey(IrfSouthAfrica, related_name='interceptees', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return "{} ({})".format(self.person.full_name, self.id)
    
    def set_parent(self, the_parent):
        self.interception_record = the_parent