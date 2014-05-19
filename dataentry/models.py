from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from accounts.models import Account


def set_weight(self, weight):
    self.weight = weight
    return self
models.BooleanField.set_weight = set_weight


class InterceptionRecord(models.Model):
    form_entered_by = models.ForeignKey(Account, related_name='irfs_entered')
    date_form_received = models.DateTimeField()

    irf_number = models.IntegerField('IRF #:')
    date_time_of_interception = models.DateTimeField('Date/Time:')

    number_of_victims = models.IntegerField('# of victims:')
    number_of_traffickers = models.IntegerField('# of traffickers')

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

    talked_to_brother = models.BooleanField('Own brother', default=False)
    talked_to_sister = models.BooleanField('Own sister', default=False)
    talked_to_father = models.BooleanField('Own father', default=False)
    talked_to_mother = models.BooleanField('Own mother', default=False)
    talked_to_grandparent = models.BooleanField('Own grandparent', default=False)
    talked_to_aunt_uncle = models.BooleanField('Own aunt / uncle', default=False)
    talked_to_other = models.BooleanField('Other', default=False)
    talked_to_other_value = models.CharField(max_length=255, blank=True)

    reported_total_red_flags = models.IntegerField('Reported Total Red Flag Points:', null=True, blank=True)

    # How did you make interception?
    contact_noticed = models.BooleanField('Contact', default=False)
    contact_hotel_owner = models.BooleanField('Hotel owner', default=False)
    contact_rickshaw_driver = models.BooleanField('Rickshaw driver', default=False)
    contact_taxi_driver = models.BooleanField('Taxi driver', default=False)
    contact_bus_driver = models.BooleanField('Bus driver', default=False)
    contact_church_member = models.BooleanField('Church member', default=False)
    contact_other_ngo = models.BooleanField('Other NGO', default=False)
    contact_police = models.BooleanField('Police', default=False)
    contact_subcommittee_member = models.BooleanField('Subcommittee member', default=False)
    contact_other = models.BooleanField('Other', default=False)
    contact_other_value = models.CharField(max_length=255, blank=True)

    # Did you pay this contact for the information?
    contact_paid_no = models.BooleanField('No', default=False)
    contact_paid_yes = models.BooleanField('Yes', default=False)
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
    name_come_up_before_yes = models.BooleanField('Yes', default=False)
    name_come_up_before_no = models.BooleanField('No', default=False)
    name_come_up_before_yes_value = models.CharField('If yes, write the # from the table above:', max_length=255, blank=True)
    scan_and_submit_same_day = models.BooleanField('Scan and submit to THN the same day', default=False)

    # Type of Intercept
    INTERCEPT_TYPE_CHOICES = [
        ('gulf-countries', 'Gulf Countries'),
        ('india-trafficking', 'India Trafficking'),
        ('unsafe-migration', 'Unsafe Migration'),
        ('circus', 'Circus'),
        ('runaway', 'Runaway'),
    ]
    interception_type = models.CharField(max_length=30, choices=INTERCEPT_TYPE_CHOICES, blank=True)

    trafficker_taken_into_custody = models.CharField('Was any trafficker taken into police custody? If yes, write the # from the table above:', max_length=255, default='', blank=True)
    how_sure_was_trafficking = models.CharField('How sure are you that it was trafficking case?', max_length=5, default='', blank=True)

    has_signature = models.BooleanField('Scanned form has signature?', default=False)

    scanned_form = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='scanned_forms', default='', blank=True)

    def calculate_total(self):
        total = 0
        for field in self._meta.fields:
            if type(field) == models.BooleanField:
                value = getattr(self, field.name)
                if value is True:
                    if hasattr(field, 'weight'):
                        total += field.weight

        return total


class Interceptee(models.Model):
    KIND_CHOICES = [
        ('v', 'Victim'),
        ('t', 'Trafficker'),
    ]
    GENDER_CHOICES = [
        ('f', 'F'),
        ('m', 'M'),
    ]
    photo = models.ImageField(upload_to='interceptee_photos', default='', blank=True)
    photo_thumbnail = ImageSpecField(source='photo',
                                     processors=[ResizeToFill(200, 200)],
                                     format='JPEG',
                                     options={'quality': 80})
    interception_record = models.ForeignKey(InterceptionRecord, related_name='interceptees')
    kind = models.CharField(max_length=4, choices=KIND_CHOICES)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=4, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    district = models.CharField(max_length=255, blank=True)
    vdc = models.CharField(max_length=255, blank=True)
    phone_contact = models.CharField(max_length=255, blank=True)
    relation_to = models.CharField(max_length=255, blank=True)


class VictimInterview(models.Model):
    vif_number = models.IntegerField('VIF #:')
    date_time = models.DateTimeField('Date/Time:')

    number_of_victims = models.IntegerField('# of victims:', null=True, blank=True)
    number_of_traffickers = models.IntegerField('# of traffickers', null=True, blank=True)

    location = models.CharField(max_length=255, blank=True)
    interviewer = models.CharField(max_length=255, blank=True)

    # 1. Victim & Family Information
    victim_name = models.CharField('Name', max_length=255)

    BOOL_CHOICES = [
        (False, 'No'),
        (True, 'Yes'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    victim_gender = models.CharField('Gender', choices=GENDER_CHOICES, max_length=12)

    victim_address_district = models.CharField('District', max_length=255, blank=True)
    victim_address_vdc = models.CharField('VDC', max_length=255, blank=True)
    victim_address_ward = models.CharField('Ward #', max_length=255, blank=True)
    victim_phone = models.CharField('Phone #', max_length=255, blank=True)
    victim_age = models.CharField('Age', max_length=255, blank=True)
    victim_height = models.CharField('Height(ft)', max_length=255, blank=True)
    victim_weight = models.CharField('Weight(kg)', max_length=255, blank=True)

    CASTE_CHOICES = [
        ('magar', 'Magar'),
        ('jaisi', 'Jaisi'),
        ('thakuri', 'Thakuri'),

        ('brahmin', 'Brahmin'),
        ('chhetri', 'Chhetri'),
        ('newar', 'Newar'),

        ('tamang', 'Tamang'),
        ('mongolian', 'Mongolian'),
        ('muslim', 'Muslim'),

        ('madeshi/terai', 'Madeshi / Terai Ethnic Group'),
        ('dalit', 'Dalit / under-priviledged'),

        ('other', 'Other'),
    ]
    victim_caste = models.CharField('Caste', choices=CASTE_CHOICES, max_length=30, blank=True)
    victim_caste_other_value = models.CharField('Other', max_length=255, blank=True)

    OCCUPATION_CHOICES = [
        ('unemployed', 'Unemployed'),
        ('farmer', 'Farmer'),
        ('wage-laborer', 'Wage-laborer'),
        ('business-owner', 'Business Owner'),
        ('migrant-worker', 'Migrant Worker'),
        ('tailoring', 'Tailoring'),
        ('housewife', 'Housewife'),
        ('animal-husbandry', 'Animal Husbandry'),
        ('domestic-work', 'Domestic Work'),
        ('shopkeeper', 'Shopkeeper'),
        ('hotel', 'Hotel'),
        ('factory', 'Factory'),
        ('other', 'Other'),
    ]
    victim_occupation = models.CharField('What is your occupation?', choices=OCCUPATION_CHOICES, max_length=50, blank=True)
    victim_occupation_other_value = models.CharField('Other', max_length=255, blank=True)

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widow', 'Widow'),
        ('divorced', 'Divorced'),
        ('husband-has-other-wives', 'Husband has other wives'),
        ('abandoned-by-husband', 'Abandoned by husband'),
    ]
    victim_marital_status = models.CharField('Marital Status', choices=MARITAL_STATUS_CHOICES, max_length=50, blank=True)

    victim_lives_with_own_parents = models.BooleanField('Own Parent(s)', default=False)
    victim_lives_with_husband = models.BooleanField('Husband', default=False)
    victim_lives_with_husbands_family = models.BooleanField('Husband\'s family', default=False)
    victim_lives_with_friends = models.BooleanField('Friends', default=False)
    victim_lives_with_alone = models.BooleanField('Alone', default=False)
    victim_lives_with_other_relative = models.BooleanField('Other Relative', default=False)
    victim_lives_with_other = models.BooleanField('Other', default=False)
    victim_lives_with_other_value = models.CharField(max_length=255, blank=True)

    victim_num_in_family = models.IntegerField('How many people are in your (own) family?', null=True, blank=True)

    GUARDIAN_CHOICES = [
        ('own-parents', 'Own Parent(s)'),
        ('husband', 'Husband'),
        ('other-relative', 'Other Relative'),
        ('non-relative', 'Non-relative'),
        ('no-one', 'No one (I have no guardian)'),
    ]
    victim_primary_guardian = models.CharField('Who is your primary guardian?', choices=GUARDIAN_CHOICES, max_length=50, blank=True)

    victim_guardian_address_district = models.CharField('District', max_length=255, blank=True)
    victim_guardian_address_vdc = models.CharField('VDC', max_length=255, blank=True)
    victim_guardian_address_ward = models.CharField('Ward #', max_length=255, blank=True)
    victim_guardian_phone = models.CharField('Phone #', max_length=255, blank=True)

    PARENTS_MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widow', 'Widow'),
        ('father-has-other-wives', 'My father has other wives'),
        ('separated', 'Separated (Legally married)'),
        ('divorced', 'Divorced'),
    ]
    victim_parents_marital_status = models.CharField('What is parents\' marital status?', choices=PARENTS_MARITAL_STATUS_CHOICES, max_length=50, blank=True)

    EDUCATION_LEVEL_CHOICES = [
        ('none', 'None'),
        ('only-informal-adult', 'Only informal (adult)'),
        ('primary-only', 'Primary only'),
        ('grade-4-8', 'Grade 4-8'),
        ('grade-9-10', 'Grade 9-10'),
        ('slc', 'SLC'),
        ('11-12', '11-12'),
        ('bachelors', 'Bachelors'),
        ('masters', 'Masters'),
    ]
    victim_education_level = models.CharField('Education Level', choices=EDUCATION_LEVEL_CHOICES, max_length=50, blank=True)

    victim_is_literate = models.NullBooleanField('Is the victim literate?',  choices=BOOL_CHOICES, null=True)

    # 2. Migration Plans
    migration_plans_education = models.BooleanField('Education', default=False)
    migration_plans_travel_tour = models.BooleanField('Travel / Tour', default=False)
    migration_plans_shopping = models.BooleanField('Shopping', default=False)
    migration_plans_eloping = models.BooleanField('Eloping', default=False)
    migration_plans_arranged_marriage = models.BooleanField('Arranged Marriage', default=False)
    migration_plans_meet_own_family = models.BooleanField('Meet your own family', default=False)
    migration_plans_visit_brokers_home = models.BooleanField('Visit broker\'s home', default=False)
    migration_plans_medical_treatment = models.BooleanField('Medical treatment', default=False)
    migration_plans_job_broker_did_not_say = models.BooleanField('Job - Broker did not say what job', default=False)
    migration_plans_job_baby_care = models.BooleanField('Job - Baby Care', default=False)
    migration_plans_job_factory = models.BooleanField('Job - Factory', default=False)
    migration_plans_job_hotel = models.BooleanField('Job - Hotel', default=False)
    migration_plans_job_shop = models.BooleanField('Job - Shop', default=False)
    migration_plans_job_laborer = models.BooleanField('Job - Laborer', default=False)
    migration_plans_job_brothel = models.BooleanField('Job - Brothel', default=False)
    migration_plans_job_household = models.BooleanField('Job - Household', default=False)
    migration_plans_job_other = models.BooleanField('Job - Other', default=False)
    migration_plans_job_value = models.CharField(max_length=255, blank=True)
    migration_plans_other = models.BooleanField('Other', default=False)
    migration_plans_other_value = models.CharField(max_length=255, blank=True)

    primary_motivation_support_myself = models.BooleanField('Support myself', default=False)
    primary_motivation_support_family = models.BooleanField('Support family', default=False)
    primary_motivation_personal_debt = models.BooleanField('Personal Debt', default=False)
    primary_motivation_family_debt = models.BooleanField('Family Debt', default=False)
    primary_motivation_love_marriage = models.BooleanField('Love / Marriage', default=False)
    primary_motivation_bad_home_marriage = models.BooleanField('Bad home / marriage', default=False)
    primary_motivation_get_an_education = models.BooleanField('Get an education', default=False)
    primary_motivation_tour_travel = models.BooleanField('Tour / Travel', default=False)
    primary_motivation_didnt_know = models.BooleanField('Didn\'t know I was going abroad', default=False)
    primary_motivation_other = models.BooleanField('Other', default=False)
    primary_motivation_other_value = models.CharField(max_length=255, blank=True)

    WHERE_GOING_REGION_CHOICES = [
        ('india', 'India'),
        ('gulf-other', 'Gulf / Other'),
    ]
    victim_where_going_region = models.CharField('Where were you going?', choices=WHERE_GOING_REGION_CHOICES, max_length=255, blank=True)

    WHERE_GOING_CHOICES = [
        ('delhi', 'Delhi'),
        ('mumbai', 'Mumbai'),
        ('surat', 'Surat'),
        ('rajastan', 'Rajastan'),
        ('kolkata', 'Kolkata'),
        ('pune', 'Pune'),
        ('jaipur', 'Jaipur'),
        ('bihar', 'Bihar'),
        ('did-not-know-india', 'Did Not Know'),
        ('other-india', 'Other'),
        ('lebanon', 'Lebanon'),
        ('dubai', 'Dubai'),
        ('malaysia', 'Malaysia'),
        ('oman', 'Oman'),
        ('saudi-arabia', 'Saudi Arabia'),
        ('kuwait', 'Kuwait'),
        ('qatar', 'Qatar'),
        ('did-not-know-gulf', 'Did Not Know'),
        ('other-gulf', 'Other'),
    ]
    victim_where_going = models.CharField(choices=WHERE_GOING_CHOICES, max_length=255, blank=True)
    victim_where_going_other_gulf_value = models.CharField(max_length=255, blank=True)
    victim_where_going_other_india_value = models.CharField(max_length=255, blank=True)

    manpower_involved = models.BooleanField('Was a manpower involved?', default=False)
    victim_recruited_in_village = models.BooleanField('Did someone recruit you in your village and persuade you to abroad?', choices=BOOL_CHOICES)

    BROKERS_RELATION_CHOICES = [
        ('own-dad', 'Own dad'),
        ('own-mom', 'Own mom'),
        ('own-uncle', 'Own uncle'),
        ('own-aunt', 'Own aunt'),
        ('own-bro', 'Own bro'),
        ('own-sister', 'Own sister'),
        ('other-relative', 'Other relative'),
        ('friend', 'Friend'),
        ('agent', 'Agent'),
        ('husband', 'Husband'),
        ('boyfriend', 'Boyfriend'),
        ('neighbor', 'Neighbor'),
        ('recently-met', 'Recently met'),
        ('contractor', 'Contractor'),
        ('other', 'Other'),
    ]
    brokers_relation_to_victim = models.CharField('Broker\'s Relation to victim', choices=BROKERS_RELATION_CHOICES, max_length=255, blank=True)
    brokers_relation_to_victim_other_value = models.CharField(max_length=255, blank=True)

    victim_married_to_broker_years = models.PositiveIntegerField('Years', null=True, blank=True)
    victim_married_to_broker_months = models.PositiveIntegerField('Months', null=True, blank=True)

    HOW_MET_BROKER_CHOICES = [
        ('broker-from-community', 'Broker is from my community'),
        ('at-work', 'At work'),
        ('at-school', 'At school'),
        ('job-advertisement', 'Job advertisement'),
        ('he-approached-me', 'He approached me'),
        ('through-friends', 'Through friends'),
        ('through-family', 'Through family'),
        ('at-wedding', 'At Wedding'),
        ('in-vehicle', 'In a Vehicle'),
        ('in-hospital', 'In a Hospital'),
        ('went-myself', 'Went to him myself'),
        ('called-mobile', 'Called my mobile'),
        ('other', 'Other'),
    ]
    victim_how_met_broker = models.CharField('How did you meet the broker?', choices=HOW_MET_BROKER_CHOICES, max_length=255, blank=True)
    victim_how_met_broker_other_value = models.CharField(max_length=255, blank=True)
    victim_how_met_broker_mobile_explanation = models.TextField(blank=True)

    victim_how_long_known_broker_years = models.PositiveIntegerField('Years', null=True, blank=True)
    victim_how_long_known_broker_months = models.PositiveIntegerField('Months', null=True, blank=True)

    HOW_EXPENSE_WAS_PAID_CHOICES = [
        ('i-paid-myself', 'I paid the expenses myself'),
        ('broker-paid', 'The broker paid all the expenses'),
        ('gave-money-to-broker', 'I gave a sum of money to the broker'),
        ('broker-paid-and-must-repay', 'The broker paid the expenses and I have to pay him back'),
    ]
    victim_how_expense_was_paid = models.CharField(choices=HOW_EXPENSE_WAS_PAID_CHOICES, max_length=255, blank=True)
    victim_how_expense_was_paid_amount = models.DecimalField('Amount', max_digits=10, decimal_places=2, null=True, blank=True)

    BROKER_WORKS_CHOICES = [
        ('no', 'No'),
        ('yes', 'Yes'),
        ('dont-know', 'Don\'t Know'),
    ]
    broker_works_in_job_location = models.CharField(max_length=255, choices=BROKER_WORKS_CHOICES, blank=True)
    amount_victim_would_earn = models.DecimalField('Amount', max_digits=10, decimal_places=2, null=True, blank=True)

    number_broker_made_similar_promises_to = models.PositiveIntegerField(null=True, blank=True)

    # Section 4

    victim_first_time_crossing_border = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    PRIMARY_MEANS_OF_TRAVEL_CHOICES = [
        ('tourist-bus', 'Tourist Bus'),
        ('motorbike', 'Motorbike'),
        ('private-car', 'Private Car'),
        ('local-bus', 'Local Bus'),
        ('microbus', 'Microbus'),
        ('plane', 'Plane'),
        ('other', 'Other'),
    ]
    victim_primary_means_of_travel = models.CharField('Primary means of travel?', choices=PRIMARY_MEANS_OF_TRAVEL_CHOICES, max_length=255)
    victim_primary_means_of_travel_other_value = models.CharField(max_length=255, blank=True)

    victim_stayed_somewhere_between = models.BooleanField(choices=BOOL_CHOICES)

    victim_how_long_stayed_between_days = models.PositiveIntegerField('Days', null=True, blank=True)
    victim_how_long_stayed_between_start_date = models.DateField('Start Date', null=True, blank=True)

    victim_was_hidden = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    victim_was_hidden_explanation = models.TextField(blank=True)

    victim_was_free_to_go_out = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    victim_was_free_to_go_out_explanation = models.TextField(blank=True)

    how_many_others_in_situation = models.PositiveIntegerField(null=True, blank=True)

    others_in_situation_age_of_youngest = models.PositiveIntegerField(null=True, blank=True)

    passport_made_no_passport_made = models.BooleanField('No passport made', default=False)
    passport_made_real_passport_made = models.BooleanField('Real passport made', default=False)
    passport_made_false_name = models.BooleanField('Passport included a false name', default=False)
    passport_made_false_info = models.BooleanField('Passport included other false info', default=False)
    passport_made_was_fake = models.BooleanField('Passport was fake', default=False)

    victim_passport_with_broker = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    abuse_happened_sexual_harassment = models.BooleanField('Sexual Harassment', default=False)
    abuse_happened_sexual_abuse = models.BooleanField('Sexual Abuse', default=False)
    abuse_happened_physical_abuse = models.BooleanField('Physical Abuse', default=False)
    abuse_happened_threats = models.BooleanField('Threats', default=False)
    abuse_happened_denied_food = models.BooleanField('Denied Proper Food', default=False)
    abuse_happened_forced_drugs = models.BooleanField('Forced to take Drugs', default=False)

    abuse_happened_by_whom = models.TextField('By whom?', blank=True)
    abuse_happened_explanation = models.TextField('Explain', blank=True)

    TRAVELED_WITH_BROKER_COMPANION_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('broker-took-to-border', 'Broker took me to border'),
    ]
    victim_traveled_with_broker_companion = models.CharField(max_length=255, choices=TRAVELED_WITH_BROKER_COMPANION_CHOICES, blank=True)

    companion_with_when_intercepted = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    planning_to_meet_companion_later = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    MONEY_CHANGED_HANDS_BROKER_COMPANION_CHOICES = [
        ('no', 'No'),
        ('dont-know', 'Don\'t know'),
        ('broker-gave-money', 'Broker gave money to the companion'),
        ('companion-gave-money', 'Companion gave money to the broker'),
    ]
    money_changed_hands_broker_companion = models.CharField(max_length=255, choices=MONEY_CHANGED_HANDS_BROKER_COMPANION_CHOICES, blank=True)

    # 5. Destination & India Contact

    WHO_MEETING_AT_BORDER_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('meeting-broker', 'Meeting Broker'),
        ('meeting-companion', 'Meeting Companion'),
    ]
    who_meeting_at_border = models.CharField(max_length=255, choices=WHO_MEETING_AT_BORDER_CHOICES)

    victim_knew_details_about_destination = models.BooleanField(choices=BOOL_CHOICES)

    other_involved_person_in_india = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    other_involved_husband_trafficker = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    other_involved_someone_met_along_the_way = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    other_involved_someone_involved_in_trafficking = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    other_involved_place_involved_in_trafficking = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    victim_has_worked_in_sex_industry = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    victim_place_worked_involved_sending_girls_overseas = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    # 6. Awareness & Assessment

    AWARENESS_CHOICES = [
        ('had-heard-didnt-know', 'Had heard, but never knew how bad it was until I was interception by TH'),
        ('didnt-think-was-happening', 'Knew how bad it was, but didn\'t think that was happening to her'),
        ('never-head', 'Had never heard about it'),
    ]
    awareness_before_interception = models.CharField(choices=AWARENESS_CHOICES, max_length=255)

    ATTITUDE_CHOICES = [
        ('yes-thankful', 'Yes, thankful to TH for saving her'),
        ('no-blames', 'No, blames Tiny Hands for stopping her'),
        ('doesnt-know', 'Doesn\'t Know'),
    ]
    attitude_towards_tiny_hands = models.CharField(choices=ATTITUDE_CHOICES, max_length=255)

    GOSPEL_HEARD_CHOICES = [
        ('never-heard', 'No, I have never heard'),
        ('heard-name-only', 'Has heard the name only'),
        ('had-heard-never-believed', 'Had heard the gospel but never believed'),
        ('already-believer', 'Was already a believer'),
    ]
    victim_heard_gospel = models.CharField(choices=GOSPEL_HEARD_CHOICES, max_length=255)

    GOSPEL_HEARD_CHOICES = [
        ('doesnt-believe', 'Doesn\'t believe in Jesus'),
        ('believes-no-church', 'Believes in Jesus, but doesn\'t plan to go to church'),
        ('believes-and-church', 'Believes in Jesus and plans to go to church'),
    ]
    victim_beliefs_now = models.CharField(choices=GOSPEL_HEARD_CHOICES, max_length=255, blank=True)

    tiny_hands_rating_border_staff = models.PositiveIntegerField('Border Staff polite and respectful')
    tiny_hands_rating_shelter_staff = models.PositiveIntegerField('Shelter Staff polite and respectful')
    tiny_hands_rating_trafficking_awareness = models.PositiveIntegerField('Trafficking Awareness')
    tiny_hands_rating_shelter_accommodations = models.PositiveIntegerField('Shelter Accommodations')

    how_can_we_serve_you_better = models.TextField(blank=True)

    # Section 7

    guardian_knew_was_travelling_to_india = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    family_pressured_victim = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    family_will_try_sending_again = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    victim_feels_safe_at_home = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    victim_wants_to_go_home = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    VICTIM_ABUSE_CHOICES = [
        ('never', 'Never'),
        ('rarely-minor', 'Rarely / Minor'),
        ('frequent-severe', 'Frequent / Severe'),
    ]
    victim_home_had_sexual_abuse = models.CharField(choices=VICTIM_ABUSE_CHOICES, max_length=40, blank=True)
    victim_home_had_physical_abuse = models.CharField(choices=VICTIM_ABUSE_CHOICES, max_length=40, blank=True)
    victim_home_had_emotional_abuse = models.CharField(choices=VICTIM_ABUSE_CHOICES, max_length=40, blank=True)

    GUARDIAN_FREQUENCY_CHOICES = [
        ('never', 'Never'),
        ('occasionally', 'Occasionally'),
        ('all-the-time', 'All the time'),
    ]
    victim_guardian_drinks_alcohol = models.CharField(choices=GUARDIAN_FREQUENCY_CHOICES, max_length=40, blank=True)
    victim_guardian_uses_drugs = models.CharField(choices=GUARDIAN_FREQUENCY_CHOICES, max_length=40, blank=True)

    ECONIMIC_SITUATION_CHOICES = [
        ('no-basic-needs', 'Unable to meet basic needs'),
        ('only-basic-needs', 'Able to meet only basic needs, but it is very difficult'),
        ('basic-needs-plus', 'Comfortably meet basic needs, and can afford to buy some non-essential goods/services'),
        ('wealthy', 'Wealthy'),
    ]
    victim_family_economic_situation = models.CharField(choices=ECONIMIC_SITUATION_CHOICES, max_length=40, blank=True)

    victim_had_suicidal_thoughts = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    reported_total_situational_alarms = models.PositiveIntegerField(blank=True, null=True)

    LEGAL_ACTION_CHOICES = [
        ('no', 'No'),
        ('fir-filed', 'FIR filed against'),
        ('dofe-complaint', 'DoFE complaint against'),
    ]
    legal_action_against_traffickers = models.CharField(choices=LEGAL_ACTION_CHOICES, max_length=40)
    legal_action_fir_against_value = models.CharField(max_length=255, blank=True)
    legal_action_dofe_against_value = models.CharField(max_length=255, blank=True)

    reason_no_legal_no_trafficking_suspected = models.BooleanField('No trafficking suspected', blank=True)
    reason_no_legal_not_enough_info = models.BooleanField('Police say not enough information', blank=True)
    reason_no_legal_victims_own_people = models.BooleanField('Trafficker is victim\'s own people', blank=True)
    reason_no_legal_girl_going_herself = models.BooleanField('She was going herself', blank=True)
    reason_no_legal_ran_away = models.BooleanField('Trafficker ran away', blank=True)
    reason_no_legal_victim_afraid_reputation = models.BooleanField('Victim afraid of reputation', blank=True)
    reason_no_legal_victim_afraid_safety = models.BooleanField('Victim afraid for her safety', blank=True)
    reason_no_legal_family_afraid_reputation = models.BooleanField('Family afraid of reputation', blank=True)
    reason_no_legal_family_afraid_safety = models.BooleanField('Family afraid for her safety', blank=True)
    reason_no_legal_police_bribed = models.BooleanField('Police bribed by trafficker', blank=True)
    reason_no_legal_victim_family_bribed = models.BooleanField('Victim / family bribed by trafficker', blank=True)

    reason_no_legal_interference_by_powerful_people = models.BooleanField('Interference by powerful people', blank=True)
    reason_no_legal_interference_by_powerful_people_value = models.CharField(max_length=255, blank=True)

    reason_no_legal_other = models.BooleanField('Other', blank=True)
    reason_no_legal_other_value = models.CharField(max_length=255, blank=True)

    INTERVIEWER_RECOMMENDATION_CHOICES = [
        ('send-to-guardians', 'Plan to send the girl home to stay with her guardians'),
        ('send-to-relatives', 'Plan to send the girl to stay with other relatives'),
        ('find-another-place', 'Tiny Hands needs to help her find another place to go'),
    ]
    interviewer_recommendation = models.CharField(choices=INTERVIEWER_RECOMMENDATION_CHOICES, max_length=40, blank=True)

    other_people_and_places_involved = models.NullBooleanField(choices=BOOL_CHOICES, null=True)

    has_signature = models.BooleanField('Scanned form has signature')

    case_notes = models.TextField('Case Notes', blank=True)


class VictimInterviewPersonBox(models.Model):
    BOOL_CHOICES = [
        (False, 'No'),
        (True, 'Yes'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    victim_interview = models.ForeignKey(VictimInterview, related_name='person_boxes')

    who_is_this_boss_of = models.BooleanField('boss of...', default=False)
    who_is_this_coworker_of = models.BooleanField('co-worker of...', default=False)
    who_is_this_own_relative_of = models.BooleanField('own relative of...', default=False)
    who_is_this_broker = models.BooleanField('Broker', default=False)
    who_is_this_companion = models.BooleanField('Companion', default=False)

    who_is_this_india_trafficker = models.BooleanField('India Trafficker', default=False)
    who_is_this_contact_of_husband = models.BooleanField('Contact of Husband', default=False)
    who_is_this_known_trafficker = models.BooleanField('Known Trafficker', default=False)
    who_is_this_manpower = models.BooleanField('Manpower', default=False)
    who_is_this_passport = models.BooleanField('Passport', default=False)
    who_is_this_sex_industry = models.BooleanField('Sex Industry', default=False)

    name = models.CharField('Name', max_length=255, blank=True)

    gender = models.CharField('Gender', choices=GENDER_CHOICES, max_length=12)

    address_district = models.CharField('District', max_length=255, blank=True)
    address_vdc = models.CharField('VDC', max_length=255, blank=True)
    address_ward = models.CharField('Ward #', max_length=255, blank=True)
    phone = models.CharField('Phone #', max_length=255, blank=True)
    age = models.CharField('Age', max_length=255, blank=True)
    height = models.CharField('Height(ft)', max_length=255, blank=True)
    weight = models.CharField('Weight(kg)', max_length=255, blank=True)

    PHYSICAL_DESCRIPTION_CHOICES = [
        ('kirat', 'Kirat'),
        ('sherpa', 'Sherpa'),
        ('madeshi', 'Madeshi'),
        ('pahadi', 'Pahadi'),
        ('newari', 'Newari'),
    ]
    physical_description = models.CharField('Physical Description', max_length=255, choices=PHYSICAL_DESCRIPTION_CHOICES, blank=True)

    appearance_other = models.CharField(max_length=255)

    OCCUPATION_CHOICES = [
        ('none', 'None'),

        ('agent', 'Agent (taking girls to India)'),
        ('business-owner', 'Business owner'),
        ('other', 'Other'),

        ('wage-labor', 'Wage labor'),
        ('job-in-india', 'Job in India'),
        ('job-in-gulf', 'Job in Gulf'),
        ('farmer', 'Farmer'),
        ('teacher', 'Teacher'),

        ('police', 'Police'),
        ('army', 'Army'),
        ('guard', 'Guard'),
        ('cook', 'Cook'),
        ('driver', 'Driver'),
    ]
    occupation = models.CharField('What is this person\'s occupation?', choices=OCCUPATION_CHOICES, max_length=50, blank=True)
    occupation_other_value = models.CharField(max_length=255, blank=True)

    POLITICAL_PARTY_CHOICES = [
        ('congress', 'Congress'),
        ('maoist', 'Maoist'),
        ('umn', 'UMN'),
        ('forum', 'Forum'),
        ('tarai-madesh', 'Tarai Madesh'),
        ('shadbawona', 'Shadbawona'),
        ('raprapha-nepal-thruhat', 'Raprapha Nepal Thruhat'),
        ('nepal-janadikarik-forum', 'Nepal Janadikarik Forum'),
        ('loktantrak-party', 'Loktantrak Party'),
        ('dont-know', 'Don\'t Know'),
        ('other', 'Other'),
    ]
    political_party = models.CharField('Member of a political Party?', max_length=255, choices=POLITICAL_PARTY_CHOICES, blank=True)
    political_party_other_value = models.CharField(max_length=255, blank=True)

    where_spends_time = models.TextField('Where does he spend most of his time? How can we get ahlod of or find him?', blank=True)

    # Which do you believe about him?
    interviewer_believes_has_trafficked_many_girls = models.BooleanField(default=False)
    interviewer_believes_has_trafficked_some_girls = models.BooleanField(default=False)
    interviewer_believes_is_trafficker = models.BooleanField(default=False)
    interviewer_believes_is_not_trafficker = models.BooleanField(default=False)

    victim_believes_has_trafficked_many_girls = models.BooleanField(default=False)
    victim_believes_has_trafficked_some_girls = models.BooleanField(default=False)
    victim_believes_is_trafficker = models.BooleanField(default=False)
    victim_believes_is_not_trafficker = models.BooleanField(default=False)

    associated_with_place = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    associated_with_place_value = models.IntegerField(blank=True, null=True)


class VictimInterviewLocationBox(models.Model):
    BOOL_CHOICES = [
        (False, 'No'),
        (True, 'Yes'),
    ]

    victim_interview = models.ForeignKey(VictimInterview, related_name='location_boxes')

    which_place_india_meetpoint = models.BooleanField('India Meet Point', default=False)
    which_place_manpower = models.BooleanField('Manpower', default=False)
    which_place_transit_hideout = models.BooleanField('Transit Hideout', default=False)
    which_place_destination = models.BooleanField('Destination', default=False)
    which_place_passport = models.BooleanField('Passport', default=False)
    which_place_nepal_meet_point = models.BooleanField('Nepal Meet Point', default=False)
    which_place_known_location = models.BooleanField('Known Location', default=False)
    which_place_sex_industry = models.BooleanField('Sex Industry', default=False)

    what_kind_place_persons_house = models.BooleanField('Person\'s House', default=False)
    what_kind_place_bus_station = models.BooleanField('Bus station', default=False)
    what_kind_place_train_station = models.BooleanField('Train station', default=False)
    what_kind_place_shop = models.BooleanField('Shop', default=False)
    what_kind_place_factory = models.BooleanField('Factory', default=False)
    what_kind_place_brothel = models.BooleanField('Brothel', default=False)
    what_kind_place_hotel = models.BooleanField('Hotel', default=False)

    vdc = models.CharField(max_length=255, blank=True)
    district = models.CharField(max_length=255, blank=True)
    signboard = models.CharField(max_length=255, blank=True)
    location_in_town = models.CharField(max_length=255, blank=True)

    phone = models.CharField('Phone #', max_length=255, blank=True)
    color = models.CharField(max_length=255, blank=True)
    number_of_levels = models.CharField('# of Levels', max_length=255, blank=True)
    compound_wall = models.CharField(max_length=255, blank=True)
    gate_color = models.CharField(max_length=255, blank=True)
    roof_type = models.CharField(max_length=255, blank=True)
    roof_color = models.CharField(max_length=255, blank=True)
    person_in_charge = models.CharField(max_length=255, blank=True)
    nearby_landmarks = models.CharField(max_length=255, blank=True)
    nearby_signboards = models.CharField(max_length=255, blank=True)
    other = models.CharField(max_length=255, blank=True)

    interviewer_believes_trafficked_many_girls = models.BooleanField(default=False)
    interviewer_believes_trafficked_some_girls = models.BooleanField(default=False)
    interviewer_believes_suspect_used_for_trafficking = models.BooleanField(default=False)
    interviewer_believes_not_used_for_trafficking = models.BooleanField(default=False)

    victim_believes_trafficked_many_girls = models.BooleanField(default=False)
    victim_believes_trafficked_some_girls = models.BooleanField(default=False)
    victim_believes_suspect_used_for_trafficking = models.BooleanField(default=False)
    victim_believes_not_used_for_trafficking = models.BooleanField(default=False)

    associated_with_person = models.NullBooleanField(choices=BOOL_CHOICES, null=True)
    associated_with_person_value = models.IntegerField(blank=True, null=True)
