from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from .person import Person
from .form import BaseCard
from .form import BaseForm

# Class to store an instance of the IRF data.
# This should contain data that is common for all IRFs and is not expected to be changed
class IrfCommon(BaseForm):
    irf_number = models.CharField('IRF #:', max_length=20, unique=True)
    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    location = models.CharField('Location:', max_length=255)
    date_time_of_interception = models.DateTimeField('Date/Time:')
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)
    staff_name = models.CharField('Staff Name:', max_length=255)
    
    profile = models.CharField(max_length=1024, blank=True)
    profile_children = models.BooleanField('Child(ren)', default=False)
    profile_migrant = models.BooleanField('Migrant', default=False)
    profile_other = models.CharField(max_length=255, blank=True)
    
    drugged_or_drowsy = models.BooleanField('Girl appears drugged or drowsy', default=False)
    who_in_group_husbandwife = models.BooleanField('Husband / Wife', default=False)
    married_in_past_2_weeks = models.BooleanField('Married in the past 2 weeks', default=False).set_weight(15)
    married_in_past_2_8_weeks = models.BooleanField('Married within the past 2-8 weeks', default=False).set_weight(10)
    caught_in_lie = models.BooleanField('Caught in a lie or contradiction', default=False).set_weight(35)
    other_red_flag = models.CharField(max_length=255, blank=True)
    
    group_missed_call = models.BooleanField('Missed Call', default=False)
    group_facebook = models.BooleanField('Facebook', default=False)
    group_other_website = models.CharField(max_length=127, blank=True)
    who_in_group_engaged = models.BooleanField('Engaged', default=False)
    who_in_group_dating = models.BooleanField('Dating Couple', default=False)
    wife_under_18 = models.BooleanField("Wife/fiancee is under 18", default=False)
    group_never_met_before = models.BooleanField('Meeting someone for the first time', default=False)
    relationship_to_get_married = models.BooleanField('On their way to get married ', default=False)
    relationship_arranged_by_other = models.BooleanField('Non-relatives organized their travel', default=False)
    with_non_relative = models.BooleanField('With non-relatives', default=False)
    traveling_with_someone_not_with_them = models.BooleanField('Was travelling with someone not with them', default=False)
    who_in_group_alone = models.BooleanField('Alone', default=False)
    who_in_group_relative = models.BooleanField('Own brother, sister / relative', default=False)
    who_in_group_pv_under_14 = models.BooleanField('PV is under 14', default=False)
    less_than_2_weeks_before_eloping = models.BooleanField('Less than 2 weeks before eloping', default=False)
    between_2_12_weeks_before_eloping = models.BooleanField('2-12 weeks before eloping', default=False)
    caste_not_same_as_relative = models.BooleanField('Caste not the same as alleged relative', default=False)
    waiting_likely_trafficker = models.BooleanField('Waiting for someone who fits description of trafficker', default=False)
    group_wife_girl_nepali_bengali = models.BooleanField('Wife/girl is Nepali/Bengali', default=False)
    contradiction_between_stories = models.BooleanField('Contradiction between stories', default=False)
    dont_know_or_conflicting_answers = models.BooleanField('They don’t know or provide conflicting answers', default=False)
    meeting_someone_across_border = models.BooleanField('Is meeting a someone just across border', default=False)
    met_within_past_2_months = models.BooleanField('Met within the past 2 months', default=False)
    met_on_the_way = models.BooleanField('Met on their way', default=False)
    undocumented_children_in_group = models.BooleanField('Undocumented child(ren) in the group', default=False)
    mobile_phone_taken_away = models.BooleanField('Their mobile phone was taken away', default=False)
    where_going_someone_paid_expenses = models.BooleanField('Non relatives paid for their travel', default=False)
    crossing_border_separately = models.BooleanField('Someone who is crossing border separately', default=False)
    relationship_married_two_months = models.BooleanField('During the past 2 months', default=False)
    different_ethnicities = models.BooleanField('Appear to be of different ethnicities', default=False)
    agent_sent_them_on = models.BooleanField('An agent who sent them on', default=False)
    who_in_group_broker = models.BooleanField('Broker/Other Person', default=False)
    meeting_someone_they_dont_know = models.BooleanField("Supposed to meet someone they don't know", default=False)
    
    who_in_group_adults = models.BooleanField('Adult(s)', default=False)
    who_in_group_children_with_parents = models.BooleanField('Child(ren) with parents', default=False)
    who_in_group_children_with_other_adults = models.BooleanField('Child(ren) with other adults', default=False)
    who_in_group_children_non_relative = models.BooleanField('Non-relative', default=False)
    who_in_group_children_relative = models.CharField(max_length=127, blank=True)
    who_in_group_children_alone = models.BooleanField('Child(ren) traveling alone', default=False)
    group_adult_meeting_someone_at_destination = models.BooleanField("(Adult) meeting someone at destination who they don't know at all or don't know well", default=False)
    group_met_companion_on_way = models.BooleanField('Met companion on their way', default=False)
    group_opportunity_for_child_too_good = models.BooleanField("Someone approached them with an opportunity for their child that's too good to be true", default=False)
    group_alleged_parents_conflicting_answers = models.BooleanField("Alleged parent(s) don't know or provide conflicting answers to basic questions", default=False)
    group_relation_verified = models.BooleanField('Relationship and Intention Verified', default=False)
    where_going_arranged_by_other = models.BooleanField('Non-relatives organized their travel', default=False)
    group_child_fearful = models.BooleanField('Child(ren) seem uncomfortable/fearful', default=False)
    group_child_meeting_someone_at_destination = models.BooleanField("(Child) meeting someone at destination who they don't know at all or don't know well", default=False)
    
    seen_in_last_month_in_nepal = models.BooleanField("Meeting someone she's seen in Nepal in the last month", default=False)
    waiting_for_someone_location = models.BooleanField("Waiting for someone in that location", default=False)
    girl_from_nepal_bangladesh = models.BooleanField("Girl is from Nepal or Bangladesh", default=False)
    
    meeting_someone_in_town = models.BooleanField('Meeting someone in a town', default=False)
    relationship_social_media = models.BooleanField('Met on social media', default=False)
    host_non_relative_paid = models.BooleanField('Non-relative(s) paid their travel expenses', default=False)
    
    group_stressed_confused = models.BooleanField('Person appears stressed/confused', default=False)
    who_in_group_with_kids = models.BooleanField('With kid(s) under 5 years old', default=False)
    who_in_group_albino = models.BooleanField('Albino kids', default=False)
    who_in_group_kids_under_5 = models.BooleanField('With kid(s) under 5 years old', default=False)
    relatives_organized_travel = models.BooleanField('Relative(s) organized their travel', default=False)
    relatives_paid_expenses = models.BooleanField('Relative(s) paid their travel expenses', default=False)
    
    industry = models.CharField('Industry', max_length=1024, blank=True)
    
    where_going_destination = models.CharField('Location:', max_length=1024, blank=True)
    where_going_doesnt_know = models.BooleanField("Doesn't know where they are going", default=False)  
    where_going_job = models.BooleanField('Job', default=False)
    employment_massage_parlor = models.BooleanField('Massage parlor', default=False)
    passport_with_broker = models.BooleanField('Passport is with a broker', default=False).set_weight(40)
    job_too_good_to_be_true = models.BooleanField('Job is too good to be true', default=False).set_weight(40)
    no_company_website = models.BooleanField('Could not find company website', default=False)
    not_real_job = models.BooleanField('Not a real job', default=False).set_weight(55)
    job_confirmed = models.BooleanField('Job confirmed', default=False)
    couldnt_confirm_job = models.BooleanField('Could not confirm job', default=False).set_weight(10)
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
    group_young_women_kids = models.BooleanField('Group of young women or kids', default=False)
    
    group_young_men = models.BooleanField('Young men', default=False)
    
    thailand_destination = models.CharField(max_length=127, blank=True)
    malaysia_destination = models.CharField(max_length=127, blank=True)
    work_sector_agriculture = models.BooleanField('Agriculture', default=False)
    work_sector_construction = models.BooleanField('Construction', default=False)
    work_sector_domestic_service = models.BooleanField('Domestic Services', default=False)
    work_sector_dont_know = models.BooleanField("Don't know", default=False)
    work_sector_factory = models.BooleanField('Factory', default=False)
    work_sector_fishing = models.BooleanField('Fishing', default=False)
    work_sector_hospitality = models.BooleanField('Hospitality', default=False)
    work_sector_logging = models.BooleanField('Logging', default=False)
    work_sector_other = models.CharField(max_length=127, blank=True)
    expected_earning = models.CharField(max_length=127, blank=True)
    took_out_loan = models.CharField(max_length=127, blank=True)
    recruited_broker = models.BooleanField('Broker/Agent', default=False)
    how_recruited_broker_approached = models.BooleanField('Broker approached them', default=False)
    met_broker_through_advertisement = models.BooleanField('Through advertisment', default=False)
    met_broker_online = models.CharField(max_length=127, blank=True)
    how_recruited_broker_other = models.CharField(max_length=127, blank=True)
    unwilling_to_give_info_about_broker = models.BooleanField('unwilling to give information about them', default=False)
    
    destination_lake_volta_region = models.BooleanField('Going to Lake Volta Region', default=False)
    
    where_going_visit = models.BooleanField('Visit / Family / Returning Home', default=False)
    where_going_shopping = models.BooleanField('Shopping', default=False)
    going_to_gulf_through_india = models.BooleanField('Going to Gulf for work through IndiaNetwork', default=False)
    no_bags_long_trip = models.BooleanField('No bags though claim to be going for a long time', default=False)
    shopping_overnight_stuff_in_bags = models.BooleanField('Shopping - Stuff for overnight stay in bags', default=False)
    where_going_dont_know_what_doing = models.BooleanField("Don't know the details of what they will be doing", default=False)
    where_going_running_from_india = models.BooleanField('Running away from IndiaNetwork (under 18)', default=False)
    where_going_enticed = models.BooleanField('Someone enticed them to leave', default=False)
    
    going_abroad_domestic_work = models.BooleanField('Going abroad for domestic work', default=False)
    job_just_graduated = models.BooleanField('Just graduated', default=False)
    visa_for_domestic_work = models.BooleanField('Have visa for domestic work in passport', default=False)
    job_underqualified = models.BooleanField('Extremely underqualified for job', default=False)
    job_details_changed_en_route = models.BooleanField('Job details were changed en route', default=False)
    
    young_woman_going_to_mining_town = models.BooleanField('Young woman going for a job in a mining town', default=False)
    seasonal_farm_work = models.BooleanField('Going for seasonal farm work', default=False)
    unregistered_mine = models.BooleanField('Going to work at unregistered mine', default=False)
    
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
    
    doesnt_know_going_to_india = models.BooleanField("Doesn't know she's going to India", default=False)
    where_going_treatment = models.BooleanField('Treatment', default=False)
    reluctant_treatment_info = models.BooleanField('Reluctant to give info about treatment', default=False)
    no_medical_documents = models.BooleanField('Does not have medical documents', default=False)
    fake_medical_documents = models.BooleanField('Fake Medical documents', default=False)
    no_medical_appointment = models.BooleanField('No medical appointment', default=False)
    
    going_plantation_work = models.BooleanField('Going to work at plantation', default=False)
    
    employment_salon = models.BooleanField('Salon', default=False)
    
    where_going_study = models.BooleanField('Study', default=False)
    no_enrollment_docs = models.BooleanField('No documentation of enrollment', default=False).set_weight(15)
    doesnt_know_school_name = models.BooleanField("Does not Know School's Name and location", default=False).set_weight(40)
    no_school_phone = models.BooleanField('No phone number for School', default=False).set_weight(30)
    no_school_website = models.BooleanField('No school website', default=False)
    not_enrolled_in_school = models.BooleanField('Not enrolled in school', default=False).set_weight(60)
    doesnt_speak_local_language = models.BooleanField("Doesn't speak English", default=False)
    doesnt_speak_destination_language = models.BooleanField("Doesn't speak language of destination", default=False)
    person_speaking_on_their_behalf = models.BooleanField('Person is not speaking on their own behalf / someone is speaking for them', default=False)
    distant_relative_paying_for_education = models.BooleanField('Distant relative is paying for education', default=False)
    valid_id_or_enrollment_documents = models.BooleanField('Valid ID card or enrollment documents', default=False)
    enrollment_confirmed = models.BooleanField('Enrollment confirmed', default=False)
    
    where_runaway = models.BooleanField('Runaway', default=False)
    running_away_over_18 = models.BooleanField('Running away from home (18 years or older)', default=False).set_weight(20)
    running_away_under_18 = models.BooleanField('Running away from home (under 18 years old)', default=False).set_weight(50)
    
    broker = models.ForeignKey(Person, null=True, blank=True)
    broker_company = models.CharField(max_length=127, blank=True)
    
    appearance_drug_withdrawl = models.BooleanField('Signs of Drug withdrawl', default=False)
    appearance_abuse = models.BooleanField('Signs of Abuse', default=False)
    appearance_disorientated = models.BooleanField('Disorientated/Uncertain', default=False)
    appearance_impoverished = models.BooleanField('Impoverished', default=False)
    appearance_long_jouney_little_luggage = models.BooleanField('Long journey but little luggage', default=False)
    appearance_revealing_clothing = models.BooleanField('Revealing clothing', default=False)
    appearance_avoid_officials = models.BooleanField('Avoiding officials/hesitant to talk', default=False)
    appearance_group_doesnt_know = models.BooleanField('Group that does not know each other', default=False)
    appearance_with_chaperone = models.BooleanField('With a chaperone', default=False)
    
    financial_support = models.BooleanField('Cannot support themselves financially', default=False)
    doesnt_know_travel_details = models.BooleanField('Does not know details of travel', default=False)
    no_return_ticket = models.BooleanField('No return ticket', default=False)
    in_debt_to_host = models.BooleanField('Is in debt to host/employer/recruiter', default=False)
    afraid_of_host = models.BooleanField('Afraid of host/employer/recruiter', default=False)
    being_forced = models.BooleanField('Being forced', default=False)
    contradiction_in_story = models.BooleanField('contradicction in story', default=False)
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
    visit_no_itinerary = models.BooleanField('No travel itinerary', default=False)
    visit_abnormal_short_stay = models.BooleanField('Abnormally short stay', default=False)
    visit_unaware_who_fetch = models.BooleanField('Unaware of who is fetching them from airport', default=False)
    relationship_suspect_forced_marriage = models.BooleanField('Suspect forced marriage', default=False)
    relationship_never_met = models.BooleanField('Never met in person', default=False)
    relationship_dont_speak_same_language = models.BooleanField('Do not speak the same language', default=False)
    study_school_doesnt_exist = models.BooleanField('School does not exist', default=False)
    study_doesnt_know_course_details = models.BooleanField('Does not know details of course', default=False)
    study_doesnt_know_school_details = models.BooleanField('Does not know details of school', default=False)
    study_doesnt_know_when_starts = models.BooleanField('Does not know when course starts', default=False)
    
    reluctant_family_info = models.BooleanField('Reluctant to give family info', default=False).set_weight(10)
    refuses_family_info = models.BooleanField('Will not give family info', default=False).set_weight(35)
    under_18_cant_contact_family = models.BooleanField('No family contact established', default=False).set_weight(50)
    under_18_family_doesnt_know = models.BooleanField("Family doesn't know she is going to India", default=False).set_weight(45)
    under_18_family_unwilling = models.BooleanField('Family unwilling to let her go', default=False).set_weight(60)
    talked_to_family_member = models.CharField(max_length=127, blank=True)
    
    doesnt_know_villiage_details = models.BooleanField("Doesn't know details about village", default=False)
    reluctant_villiage_info = models.BooleanField('Reluctant to give info about village', default=False)
    over_18_family_doesnt_know = models.BooleanField('Family members do not know they is going to India', default=False)
    over_18_family_unwilling = models.BooleanField('Family members unwilling to let them go', default=False)
    
    family_doesnt_know_where_going_18_23 = models.BooleanField('18-23, family does not know where they are going', default=False)
    family_unwilling_to_let_go_18_23 = models.BooleanField('18-23, family unwilling to let them go', default=False)
    over_23_family_unwilling_to_let_go = models.BooleanField('Over 23, family unwilling to let them go', default=False)
    
    family_unwilling_take_them_back = models.BooleanField('Called, family unwilling to receive them back', default=False)
    
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

    
    signs_treatment = models.BooleanField('Treatment - no documentation / knowledge', default=False)
    signs_forged_false_documentation = models.BooleanField('Forged or falsified documents', default=False)
    signs_confirmed_deception = models.BooleanField('Called place and confirmed deception', default=False)
    signs_other = models.CharField(max_length=127, blank=True)
    signs_fake_documentation = models.BooleanField('Fake documents', default=False)
    
    control_led_other_country = models.BooleanField('Led to other country without their knowledge', default=False)
    control_traveling_because_of_threat = models.BooleanField('Traveling because of a threat', default=False)
    control_owes_debt = models.BooleanField('Owes debt to person who recruited/paid travel', default=False)
    control_job = models.CharField(max_length=127, blank=True)
    control_promised_pay = models.CharField(max_length=127, blank=True)
    control_normal_pay = models.CharField(max_length=127, blank=True)
    control_promised_double = models.BooleanField('Promised pay more than double normal pay', default=False)
    control_promised_higher = models.BooleanField('Promised pay a little higher than normal pay', default=False)
    control_no_address_phone = models.BooleanField('No address / phone number (of job)', default=False)
    
    reported_total_red_flags = models.IntegerField('Reported Total Red Flag Points:', null=True, blank=True)
    computed_total_red_flags = models.IntegerField('Computed Total Red Flag Points:', null=True, blank=True)
    
    who_noticed = models.CharField(max_length=127, null=True)
    staff_who_noticed = models.CharField('Staff who noticed:', max_length=255, blank=True)
    
    which_contact = models.CharField(max_length=127, blank=True)
    name_of_contact = models.CharField(max_length=127, default='', blank=True)
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
    initial_signs = models.CharField(max_length=127, default='', blank=True)
    
    noticed_drugged_or_drowsy = models.BooleanField('Drugged or drowsy', default=False)
    noticed_on_train = models.BooleanField('on train', default=False)
    
    noticed_other_sign = models.CharField(max_length=127, blank=True)
    
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
    
    documentation_in_order = models.BooleanField('Documentation in order', default=False)
    no_red_flags = models.BooleanField('No red flags', default=False)
    story_consistent = models.BooleanField('Story consistent', default=False)
    details_validated_and_correted = models.BooleanField('Details were validated and corrected', default=False)
    
    child_no_affidavit = models.BooleanField('No affidavit/birth certificate', default=False)
    child_fearful = models.BooleanField('Child fearful of handler', default=False)
    child_not_escorted = models.BooleanField('Not being escorted by direct relative', default=False)
    child_handler_inconsistent_story = models.BooleanField('Handler stories are inconsistent', default=False)
    child_handler_false_claims = models.BooleanField('Handler falsely claims to be relative', default=False)
    child_handler_criminal = models.BooleanField('Handler involved in criminal activity', default=False)
    child_relative_contacted  = models.CharField(max_length=127, default='', blank=True)
    
    entry_allowed = models.BooleanField('Entry allowed', default=False)
    entry_refused = models.BooleanField('Entry refused', default=False)
    transit_allowed = models.BooleanField('Transit allowed', default=False)
    transit_refused = models.BooleanField('Transit refused', default=False)
    believe_they_are_pvot = models.NullBooleanField('Do they believe they are PVOT?', null=True)
    require_assistance = models.NullBooleanField('Do they require assistance?', null=True)
    ims_case_number = models.CharField(max_length=127, default='', blank=True)
    case_report = models.BooleanField('Case report', default=False)
    cif = models.BooleanField('CIF', default=False)
    
    immigration_lj_entry = models.CharField(max_length=127, null=True)
    immigration_lj_transit = models.CharField(max_length=127, null=True)
    immigration_lj_exit = models.CharField(max_length=127, null=True)
    immigration_entry = models.CharField(max_length=127, null=True)
    immigration_transit = models.CharField(max_length=127, null=True)
    immigration_exit = models.CharField(max_length=127, null=True)
    immigration_case_number = models.CharField(max_length=127, null=True)
    
    type_of_intercept = models.CharField(max_length=127, null=True)
    case_notes = models.TextField('Case Notes', blank=True)
    interception_made = models.CharField(max_length=127, null=True)
    handed_over_to =  models.CharField(max_length=127, default='', blank=True)
    
    HOW_SURE_TRAFFICKING_CHOICES = [
        (1, '1 - Not at all sure'),
        (2, '2 - Unsure but suspects it'),
        (3, '3 - Somewhat sure'),
        (4, '4 - Very sure'),
        (5, '5 - Absolutely sure'),
    ]
    how_sure_was_trafficking = models.IntegerField(
        'How sure are you that it was trafficking case?',
        choices=HOW_SURE_TRAFFICKING_CHOICES, null=True)
    
    convinced_by_staff = models.CharField(max_length=127, blank=True)
    convinced_by_family = models.CharField(max_length=127, blank=True)
    convinced_family_phone = models.CharField(max_length=127, blank=True)
    convinced_by_police = models.CharField(max_length=127, blank=True)
    
    evidence_categorization = models.CharField(max_length=127, null=True)
    reason_for_intercept = models.TextField('Primary reason for intercept', blank=True)
    
    call_subcommittee = models.BooleanField('Call Subcommittee Chairperson/Vice-Chairperson/Secretary', default=False)
    call_project_manager = models.BooleanField('Call Project Manager to confirm intercept', default=False)
    
    rescue = models.BooleanField('Rescue', default=False)

    has_signature = models.BooleanField('Scanned form has signature?', default=False)
    
    #Logbook
    logbook_received = models.DateField(null=True)
    logbook_incomplete_questions = models.CharField(max_length=127, blank=True)
    logbook_incomplete_sections = models.CharField(max_length=127, blank=True)
    logbook_information_complete = models.DateField(null=True)
    logbook_notes = models.TextField('Logbook Notes', blank=True)
    logbook_submitted = models.DateField(null=True)
    
    logbook_first_verification = models.CharField(max_length=127, blank=True)
    logbook_first_reason = models.TextField('First Reason', blank=True)
    logbook_followup_call = models.CharField(max_length=127, blank=True)
    logbook_first_verification_date = models.DateField(null=True)
    logbook_first_verification_name = models.CharField(max_length=127, blank=True)
    
    logbook_leadership_review = models.CharField(max_length=127, blank=True)
    logbook_second_verification = models.CharField(max_length=127, blank=True)
    logbook_second_reason = models.TextField('Second Reason', blank=True)
    logbook_second_verification_date = models.DateField(null=True)
    logbook_second_verification_name = models.CharField(max_length=127, blank=True)
    
    logbook_champion_verification = models.BooleanField('Champion verification', default=False)
    
    logbook_back_corrected = models.TextField('Back Corrected', blank=True)
    
    def get_key(self):
        return self.irf_number
    
    def get_form_type_name(self):
        return 'IRF'
    
    def get_form_date(self):
        return self.date_time_of_interception.date()
    
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
    