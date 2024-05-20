# TODO: Consider refactoring of models...

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db.models import JSONField

class AnalyzedPerson:
    def __init__(self, full_photo, face_photo=None, face_analysis=None):
        self.full_photo = full_photo
        self.face_photo = face_photo
        self.face_analysis = face_analysis


class MatchingPerson():
    def __init__(self, full_name, person_id, gender, role, face_photo, full_photo, irf_number, nationality, age_at_interception, date_of_interception, face_analysis, face_distance):
        self.full_name = full_name 
        self.person_id = person_id 
        self.gender = gender 
        self.role = role 
        self.irf_number = irf_number 
        self.nationality = nationality 
        self.age_at_interception = age_at_interception 
        self.date_of_interception = date_of_interception 
        self.face_analysis = face_analysis 
        self.face_distance = face_distance 
        self.face_photo = face_photo 
        self.full_photo = full_photo 


class MatchingData():
    def __init__(self, analyzedPerson, matchingPersons):
        self.analyzedPerson = analyzedPerson
        self.matchingPersons = matchingPersons


class DataentryIntercepteecommon(models.Model):
    id = models.IntegerField(primary_key=True)
    relation_to = models.CharField(max_length=255)
    interception_record = models.ForeignKey(
        'DataentryIrfcommon', on_delete=models.DO_NOTHING)
    # NOTE: Made assumption that person field is unique in this table to work around lack of foreign key from face_encoding on dataentry_person in database
    person = models.ForeignKey(
        'DataentryPerson', on_delete=models.DO_NOTHING, blank=True, null=True, unique=True)
    not_physically_present = models.CharField(max_length=127)
    consent_to_use_information = models.CharField(
        max_length=255, blank=True, null=True)
    consent_to_use_photo = models.CharField(
        max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataentry_intercepteecommon'
 
    def __str__(self):
        return f'DataentryIntercepteecommon: {self.id}, {self.person.id}'

class FaceEncoding(models.Model):
    person = models.ForeignKey(DataentryIntercepteecommon, primary_key=True,
                                  to_field="person_id", db_column="person_id", on_delete=models.DO_NOTHING)
    # person = models.IntegerField(primary_key=True)
    # This field type is a guess.
    face_encoding = ArrayField(models.FloatField(
        blank=True), blank=True, size=128)
    outcome = models.TextField(blank=True)

    class Meta:
        managed = False  # TODO: remove me
        db_table = 'face_encodings'

        def __str__(self):
            return self.person_id


class DataentryBorderstation(models.Model):
    id = models.IntegerField(primary_key=True)
    station_code = models.CharField(unique=True, max_length=3)
    station_name = models.CharField(max_length=100)
    date_established = models.DateField(blank=True, null=True)
    has_shelter = models.BooleanField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    open = models.BooleanField()
    operating_country = models.ForeignKey(
        'DataentryCountry', on_delete=models.DO_NOTHING, blank=True, null=True)
    time_zone = models.CharField(max_length=127)
    auto_number = models.CharField(max_length=127, blank=True, null=True)
    features = models.CharField(max_length=512)
    project_category = models.ForeignKey(
        'DataentryProjectcategory', on_delete=models.DO_NOTHING, blank=True, null=True)
    mdf_project = models.ForeignKey(
        'self', on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataentry_borderstation'


class DataentryCountry(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom_level = models.IntegerField(blank=True, null=True)
    date_time_updated = models.DateTimeField()
    currency = models.CharField(max_length=127)
    mdf_sender_email = models.CharField(max_length=127)
    verification_goals = JSONField(blank=True, null=True)
    verification_start_month = models.IntegerField(blank=True, null=True)
    verification_start_year = models.IntegerField(blank=True, null=True)
    options = JSONField(blank=True, null=True)
    region = models.ForeignKey('DataentryRegion', on_delete=models.DO_NOTHING)
    prior_arrests = models.IntegerField()
    prior_convictions = models.IntegerField()
    prior_intercepts = models.IntegerField()
    enable_all_locations = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'dataentry_country'

    def __str__(self):
        return self.name


class DataentryIrfcommon(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=20)
    date_time_entered_into_system = models.DateTimeField()
    date_time_last_updated = models.DateTimeField()
    irf_number = models.CharField(unique=True, max_length=20)
    number_of_victims = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=255)
    number_of_traffickers = models.IntegerField(blank=True, null=True)
    staff_name = models.CharField(max_length=255)
    control_drugged_or_drowsy = models.BooleanField()
    control_married_in_past_2_weeks = models.BooleanField()
    control_married_in_past_2_8_weeks = models.BooleanField()
    evade_caught_in_lie = models.BooleanField()
    vulnerability_group_missed_call = models.BooleanField()
    vulnerability_group_facebook = models.BooleanField()
    vulnerability_group_other_website = models.CharField(max_length=127)
    control_wife_under_18 = models.BooleanField()
    vulnerability_group_never_met_before = models.BooleanField()
    control_relationship_to_get_married = models.BooleanField()
    control_traveling_with_someone_not_with_them = models.BooleanField()
    control_less_than_2_weeks_before_eloping = models.BooleanField()
    control_contradiction_stories = models.BooleanField()
    vulnerability_met_on_the_way = models.BooleanField()
    control_mobile_phone_taken_away = models.BooleanField()
    control_where_going_someone_paid_expenses = models.BooleanField()
    where_going_destination = models.CharField(max_length=1024)
    vulnerability_where_going_doesnt_know = models.BooleanField()
    control_passport_with_broker = models.BooleanField()
    control_not_real_job = models.BooleanField()
    evade_couldnt_confirm_job = models.BooleanField()
    evade_no_bags_long_trip = models.BooleanField()
    control_job_underqualified = models.BooleanField()
    evade_job_details_changed_en_route = models.BooleanField()
    evade_visa_misuse = models.BooleanField()
    vulnerability_supporting_documents_one_way_ticket = models.BooleanField()
    vulnerability_doesnt_speak_destination_language = models.BooleanField()
    vulnerability_person_speaking_on_their_behalf = models.BooleanField()
    evade_appearance_avoid_officials = models.BooleanField()
    vulnerability_afraid_of_host = models.BooleanField()
    evade_study_doesnt_know_school_details = models.BooleanField()
    vulnerability_refuses_family_info = models.BooleanField()
    vulnerability_under_18_family_doesnt_know = models.BooleanField()
    control_under_18_family_unwilling = models.BooleanField()
    talked_to_family_member = models.CharField(max_length=127)
    control_reported_total_red_flags = models.IntegerField(
        blank=True, null=True)
    computed_total_red_flags = models.IntegerField(blank=True, null=True)
    who_noticed = models.CharField(max_length=127, blank=True, null=True)
    staff_who_noticed = models.CharField(max_length=255)
    which_contact = models.CharField(max_length=127)
    contact_paid = models.BooleanField(null=True)
    contact_paid_how_much = models.CharField(max_length=255)
    evade_noticed_carrying_full_bags = models.BooleanField()
    control_status_known_trafficker = models.BooleanField()
    case_notes = models.TextField()
    how_sure_was_trafficking = models.IntegerField(blank=True, null=True)
    convinced_by_staff = models.CharField(max_length=127)
    convinced_by_family = models.CharField(max_length=127)
    convinced_by_police = models.CharField(max_length=127)
    evidence_categorization = models.CharField(
        max_length=127, blank=True, null=True)
    reason_for_intercept = models.TextField()
    call_subcommittee = models.BooleanField()
    call_project_manager = models.BooleanField()
    has_signature = models.BooleanField()
    logbook_received = models.DateField(blank=True, null=True)
    logbook_incomplete_questions = models.CharField(max_length=127)
    logbook_incomplete_sections = models.CharField(max_length=127)
    logbook_information_complete = models.DateField(blank=True, null=True)
    logbook_notes = models.TextField()
    logbook_submitted = models.DateField(blank=True, null=True)
    logbook_first_verification = models.CharField(max_length=127)
    logbook_first_reason = models.TextField()
    logbook_followup_call = models.CharField(max_length=127)
    logbook_first_verification_date = models.DateField(blank=True, null=True)
    verified_evidence_categorization = models.CharField(max_length=127)
    logbook_second_reason = models.TextField()
    verified_date = models.DateField(blank=True, null=True)
    form_entered_by = models.ForeignKey(
        'AccountsAccount', on_delete=models.DO_NOTHING, blank=True, null=True)
    station = models.ForeignKey(
        'DataentryBorderstation', on_delete=models.DO_NOTHING)
    control_job = models.CharField(max_length=127)
    control_led_other_country = models.BooleanField()
    control_no_address_phone = models.BooleanField()
    control_normal_pay = models.CharField(max_length=127)
    control_owes_debt = models.BooleanField()
    control_promised_double = models.BooleanField()
    control_promised_higher = models.BooleanField()
    control_promised_pay = models.CharField(max_length=127)
    control_traveling_because_of_threat = models.BooleanField()
    convinced_family_phone = models.CharField(max_length=127)
    industry = models.CharField(max_length=1024)
    evade_signs_confirmed_deception = models.BooleanField()
    evade_signs_forged_false_documentation = models.BooleanField()
    evade_signs_other = models.CharField(max_length=127)
    evade_signs_treatment = models.BooleanField()
    vulnerability_insufficient_resource = models.BooleanField()
    vulnerability_minor_without_guardian = models.BooleanField()
    vulnerability_family_unwilling = models.BooleanField()
    logbook_champion_verification = models.BooleanField()
    rescue = models.BooleanField()
    profile = models.CharField(max_length=1024)
    vulnerability_first_time_traveling_abroad = models.BooleanField()
    immigration_case_number = models.CharField(
        max_length=127, blank=True, null=True)
    immigration_entry = models.CharField(max_length=127, blank=True, null=True)
    immigration_exit = models.CharField(max_length=127, blank=True, null=True)
    immigration_lj_entry = models.CharField(
        max_length=127, blank=True, null=True)
    immigration_lj_exit = models.CharField(
        max_length=127, blank=True, null=True)
    immigration_lj_transit = models.CharField(
        max_length=127, blank=True, null=True)
    immigration_transit = models.CharField(
        max_length=127, blank=True, null=True)
    vulnerability_connection_host_unclear = models.BooleanField()
    vulnerability_doesnt_have_required_visa = models.BooleanField()
    vulnerability_doesnt_speak_english = models.BooleanField()
    vulnerability_non_relative_paid_flight = models.BooleanField()
    vulnerability_paid_flight_in_cash = models.BooleanField()
    evade_signs_fake_documentation = models.BooleanField()
    logbook_first_verification_name = models.CharField(max_length=127)
    logbook_second_verification_name = models.CharField(max_length=127)
    vulnerability_family_friend_arranged_travel = models.BooleanField()
    form_version = models.CharField(max_length=126, blank=True, null=True)
    date_of_interception = models.DateField(blank=True, null=True)
    time_of_interception = models.TimeField(blank=True, null=True)
    control_connected_known_trafficker = models.BooleanField()
    flight_number = models.CharField(max_length=127, blank=True, null=True)
    vulnerability_bus_driver_payment_at_destination = models.BooleanField()
    vulnerability_first_time_traveling_to_city = models.BooleanField()
    vulnerability_no_id = models.BooleanField()
    vulnerability_no_mobile_phone = models.BooleanField()
    control_abducted = models.BooleanField()
    pv_stopped_on_own = models.CharField(max_length=127)
    vulnerability_meeting_someone_met_online = models.BooleanField()
    vulnerability_travel_arranged_by_other = models.BooleanField()
    control_under_18_recruited_for_work = models.BooleanField()
    vulnerability_travel_met_recently = models.BooleanField()
    control_id_or_permit_with_broker = models.BooleanField()
    vulnerability_stranded_or_abandoned = models.BooleanField()
    control_under_16_recruited_for_work = models.BooleanField()
    has_offical_signature = models.BooleanField()
    official_name = models.CharField(max_length=127, blank=True, null=True)
    route = models.TextField()
    agreement_contract_language = models.BooleanField()
    agreement_mpa_not_bearing_cost = models.BooleanField()
    agreement_no_receipt = models.BooleanField()
    agreement_paid_above_standard = models.BooleanField()
    agreement_paid_agent = models.BooleanField()
    control_agreement_prepermission_mismatch = models.BooleanField()
    control_enticed_banned_area = models.BooleanField()
    control_enticed_non_seasonal = models.BooleanField()
    control_facilitated_via_third_country = models.BooleanField()
    control_invalid_lt = models.BooleanField()
    control_invalid_mpa = models.BooleanField()
    control_visa_misuse = models.BooleanField()
    control_women_enticed_unsave_area = models.BooleanField()
    mpa_agent_not_used = models.BooleanField()
    mpa_name = models.CharField(max_length=127, blank=True, null=True)
    mpa_phone = models.CharField(max_length=127, blank=True, null=True)
    preparation_did_not_complete = models.CharField(max_length=1024)
    preparation_other = models.CharField(max_length=127)
    preparation_unaware_of_process = models.BooleanField()
    pv_closest_contact = models.TextField()
    pv_lt_number_after_counsel = models.CharField(max_length=127)
    pv_lt_number_before_counsel = models.CharField(max_length=127)
    result_pv_changed_plans = models.CharField(
        max_length=127, blank=True, null=True)
    result_pv_local_job = models.BooleanField()
    result_pv_other_education = models.BooleanField()
    result_pv_tech_training = models.BooleanField()
    vulnerability_applied_job_doesnt_know_destination = models.BooleanField()
    vulnerability_cost_of_living_higher_than_wages = models.BooleanField()
    vulnerability_doesnt_know_job_details = models.BooleanField()
    vulnerability_doesnt_speak_local_language = models.BooleanField()
    vulnerability_going_via_india = models.BooleanField()
    vulnerability_mpa_excessive_time = models.BooleanField()
    vulnerability_using_agent = models.BooleanField()
    agent_how_contacted = models.CharField(
        max_length=127, blank=True, null=True)
    agent_is_suspect = models.CharField(max_length=127, blank=True, null=True)
    agent_who_initiated_contact = models.CharField(
        max_length=127, blank=True, null=True)
    mpa_how_contacted = models.CharField(max_length=127, blank=True, null=True)
    mpa_is_suspect = models.CharField(max_length=127, blank=True, null=True)
    mpa_who_initiated_contact = models.CharField(
        max_length=127, blank=True, null=True)
    vulnerability_different_last_name = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'dataentry_irfcommon'


class DataentryPerson(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=4)
    age = models.IntegerField(blank=True, null=True)
    phone_contact = models.CharField(max_length=255)
    address1 = models.ForeignKey(
        'DataentryAddress1', on_delete=models.DO_NOTHING, blank=True, null=True)
    address2 = models.ForeignKey(
        'DataentryAddress2', on_delete=models.DO_NOTHING, blank=True, null=True)
    alias_group = models.ForeignKey(
        'DataentryAliasgroup', on_delete=models.DO_NOTHING, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=127)
    estimated_birthdate = models.DateField(blank=True, null=True)
    address = JSONField(blank=True, null=True)
    address_notes = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    appearance = models.CharField(max_length=126, blank=True, null=True)
    arrested = models.CharField(max_length=126, blank=True, null=True)
    case_filed_against = models.CharField(
        max_length=126, blank=True, null=True)
    education = models.CharField(max_length=126, blank=True, null=True)
    guardian_name = models.CharField(max_length=126, blank=True, null=True)
    guardian_phone = models.CharField(max_length=126, blank=True, null=True)
    guardian_relationship = models.CharField(
        max_length=1024, blank=True, null=True)
    interviewer_believes = models.CharField(
        max_length=126, blank=True, null=True)
    occupation = models.CharField(max_length=126, blank=True, null=True)
    photo = models.CharField(max_length=100)
    anonymized_photo = models.CharField(max_length=126, blank=True, null=True)
    pv_believes = models.CharField(max_length=126, blank=True, null=True)
    role = models.CharField(max_length=126, blank=True, null=True)
    social_media = models.CharField(max_length=1024, blank=True, null=True)
    address_verified = models.BooleanField()
    master_set_by = models.ForeignKey(
        'AccountsAccount', on_delete=models.DO_NOTHING, blank=True, null=True)
    master_set_date = models.DateField()
    master_set_notes = models.TextField()
    phone_verified = models.BooleanField()
    address_type = models.ForeignKey(
        'DataentryAddresstype', on_delete=models.DO_NOTHING, blank=True, null=True)
    master_person = models.ForeignKey(
        'DataentryMasterperson', on_delete=models.DO_NOTHING)
    phone_type = models.ForeignKey(
        'DataentryPhonetype', on_delete=models.DO_NOTHING, blank=True, null=True)
    social_media_verified = models.BooleanField()
    social_media_type = models.ForeignKey(
        'DataentrySocialmediatype', on_delete=models.DO_NOTHING, blank=True, null=True)
    last_match_time = models.DateTimeField(blank=True, null=True)
    last_modified_time = models.DateTimeField()
    other_contact_name = models.CharField(
        max_length=126, blank=True, null=True)
    other_contact_phone = models.CharField(
        max_length=126, blank=True, null=True)
    social_media_platform = models.CharField(
        max_length=1024, blank=True, null=True)
    whatsapp = models.CharField(db_column='whatsApp', max_length=1024, blank=True,
                                null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dataentry_person'

    def __str__(self):
        return str(self.id)


class DataentryProjectcategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=127)
    sort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dataentry_projectcategory'


class DataentryRegion(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'dataentry_region'


class AccountsAccount(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    email = models.CharField(unique=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    permission_irf_view = models.BooleanField()
    permission_irf_add = models.BooleanField()
    permission_irf_edit = models.BooleanField()
    permission_vif_view = models.BooleanField()
    permission_vif_add = models.BooleanField()
    permission_vif_edit = models.BooleanField()
    permission_accounts_manage = models.BooleanField()
    permission_border_stations_view = models.BooleanField()
    permission_border_stations_add = models.BooleanField()
    permission_border_stations_edit = models.BooleanField()
    permission_address2_manage = models.BooleanField()
    date_joined = models.DateTimeField()
    activation_key = models.CharField(max_length=40)
    user_designation = models.ForeignKey(
        'AccountsDefaultpermissionsset', on_delete=models.DO_NOTHING, blank=True, null=True)
    permission_irf_delete = models.BooleanField()
    permission_vif_delete = models.BooleanField()
    permission_border_stations_delete = models.BooleanField()
    permission_receive_investigation_alert = models.BooleanField()
    permission_receive_legal_alert = models.BooleanField()
    permission_budget_add = models.BooleanField()
    permission_budget_delete = models.BooleanField()
    permission_budget_edit = models.BooleanField()
    permission_budget_view = models.BooleanField()
    permission_can_receive_mdf = models.BooleanField()
    permission_person_match = models.BooleanField()
    country_name = models.CharField(max_length=127)
    role = models.CharField(max_length=127)

    class Meta:
        managed = False
        db_table = 'accounts_account'


class DataentryAddress1(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    completed = models.BooleanField()
    latitude = models.FloatField()
    level = models.CharField(max_length=255)
    longitude = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dataentry_address1'


class DataentryAddress2(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    verified = models.BooleanField()
    canonical_name = models.ForeignKey(
        'self', models.DO_NOTHING, blank=True, null=True)
    address1 = models.ForeignKey(DataentryAddress1, models.DO_NOTHING)
    level = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'dataentry_address2'


class DataentryAddresstype(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataentry_addresstype'


class DataentryAliasgroup(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'dataentry_aliasgroup'


class DataentryMasterperson(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=4)
    birthdate = models.DateField(blank=True, null=True)
    estimated_birthdate = models.BooleanField()
    nationality = models.CharField(max_length=127)
    appearance = models.TextField()
    notes = models.TextField()
    active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'dataentry_masterperson'


class DataentryPhonetype(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataentry_phonetype'


class DataentrySocialmediatype(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dataentry_socialmediatype'


class AccountsDefaultpermissionsset(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    permission_irf_view = models.BooleanField()
    permission_irf_add = models.BooleanField()
    permission_irf_edit = models.BooleanField()
    permission_vif_view = models.BooleanField()
    permission_vif_add = models.BooleanField()
    permission_vif_edit = models.BooleanField()
    permission_accounts_manage = models.BooleanField()
    permission_border_stations_view = models.BooleanField()
    permission_border_stations_add = models.BooleanField()
    permission_border_stations_edit = models.BooleanField()
    permission_address2_manage = models.BooleanField()
    permission_irf_delete = models.BooleanField()
    permission_vif_delete = models.BooleanField()
    permission_border_stations_delete = models.BooleanField()
    permission_receive_investigation_alert = models.BooleanField()
    permission_receive_legal_alert = models.BooleanField()
    permission_budget_add = models.BooleanField()
    permission_budget_delete = models.BooleanField()
    permission_budget_edit = models.BooleanField()
    permission_budget_view = models.BooleanField()
    permission_can_receive_mdf = models.BooleanField()
    permission_person_match = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts_defaultpermissionsset'
