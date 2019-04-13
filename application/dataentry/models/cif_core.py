from django.db import models

from .person import Person
from .form import BaseCard, BaseForm
from .addresses import Address2

class CifCore(BaseForm):
    # Top
    cif_number = models.CharField('CIF #:', max_length=20, unique=True)
    number_of_victims = models.PositiveIntegerField('# of victims:', null=True, blank=True)
    staff_name = models.CharField('Staff Name:', max_length=126, null=True)
    interview_date = models.DateField(null=True)
    number_of_traffickers = models.PositiveIntegerField('# of traffickers', null=True, blank=True)
    location = models.CharField('Location:', max_length=126, null=True)
    source_of_intelligence = models.CharField('Source of intelligence:', max_length=126, null=True)
    informant_number = models.CharField('Informant #', max_length=126, null=True, blank=True)
    incident_date = models.DateField(null=True)
    pv_signed_form = models.BooleanField('PV signature', default=False)
    consent_for_fundraising = models.BooleanField('Consent for fundraising', default=False)
    
    # Main PV
    main_pv = models.ForeignKey(Person, null=True, blank=True)
    social_media = models.CharField('Social Media', max_length=1024, null=True)
    occupation = models.CharField('Occupation', max_length=126, null=True)
    education = models.CharField('Occupation', max_length=126, null=True)
    guardian_name = models.CharField('Guardian Name', max_length=126, null=True)
    guardian_phone = models.CharField('Guardian Phone', max_length=126, null=True)
    guardian_relationship = models.CharField('Guardian Relationship', max_length=1024, null=True)
    other_possible_victims = models.BooleanField('other possible victims', default=False)
    
    # Recruitment
    recruited_agency = models.BooleanField(default=False)
    recruited_agency_pb = models.CharField('Agency PB', max_length=126, null=True)
    recruited_broker = models.BooleanField(default=False)
    recruited_broker_pb = models.CharField('Broker PB', max_length=126, null=True)
    recruited_no = models.BooleanField(default=False)
    how_recruited_promised_job = models.BooleanField(default=False)
    how_recruited_married = models.BooleanField(default=False)
    how_recruited_promised_marriage = models.BooleanField(default=False)
    how_recruited_at_work = models.BooleanField(default=False)
    how_recruited_at_school = models.BooleanField(default=False)
    how_recruited_job_ad = models.BooleanField(default=False)
    how_recruited_broker_online = models.BooleanField(default=False)
    how_recruited_broker_online_pb = models.CharField(max_length=126, null=True)
    how_recruited_broker_approached = models.BooleanField(default=False)
    how_recruited_broker_approached_pb = models.CharField(max_length=126, null=True)
    how_recruited_broker_through_friends = models.BooleanField(default=False)
    how_recruited_broker_through_family = models.BooleanField(default=False)
    how_recruited_broker_called_pv = models.BooleanField(default=False)
    how_recruited_broker_other = models.CharField(max_length=126, null=True)
    known_broker_years = models.PositiveIntegerField(null=True, blank=True)
    known_broker_months = models.PositiveIntegerField(null=True, blank=True)
    known_broker_days = models.PositiveIntegerField(null=True, blank=True)
    known_broker_pb = models.CharField(max_length=126, null=True)
    married_broker_years = models.PositiveIntegerField(null=True, blank=True)
    married_broker_months = models.PositiveIntegerField(null=True, blank=True)
    married_broker_days = models.PositiveIntegerField(null=True, blank=True)
    married_broker_pb = models.CharField(max_length=126, null=True)
    travel_expenses_paid_themselves = models.BooleanField(default=False)
    travel_expenses_paid_by_broker = models.BooleanField(default=False)
    travel_expenses_paid_by_broker_pb = models.CharField(max_length=126, null=True)
    travel_expenses_paid_to_broker = models.BooleanField(default=False)
    travel_expenses_paid_to_broker_pb = models.CharField(max_length=126, null=True)
    travel_expenses_paid_by_broker_repaid = models.BooleanField(default=False)
    travel_expenses_paid_by_broker_repaid_pb = models.CharField(max_length=126, null=True)
    travel_expenses_paid_to_broker_amount = models.CharField(max_length=126, null=True)
    travel_expenses_broker_repaid_amount = models.CharField(max_length=126, null=True)
    expected_earning = models.CharField(max_length=126, null=True)
    expected_earning_pb = models.CharField(max_length=126, null=True)
    suspected_trafficker_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Travel
    purpose_for_leaving_education = models.BooleanField(default=False)
    purpose_for_leaving_travel_tour = models.BooleanField(default=False)
    purpose_for_leaving_marriage = models.BooleanField(default=False)
    purpose_for_leaving_family = models.BooleanField(default=False)
    purpose_for_leaving_medical = models.BooleanField(default=False)
    purpose_for_leaving_job_hotel = models.BooleanField(default=False)
    purpose_for_leaving_job_household = models.BooleanField(default=False)
    purpose_for_leaving_other = models.CharField(max_length=126, null=True)
    planned_destination = models.CharField(max_length=126, null=True)
    border_cross_night = models.BooleanField(default=False)
    border_cross_off_road = models.BooleanField(default=False)
    border_cross_foot = models.BooleanField(default=False)
    border_cross_vehicle = models.BooleanField(default=False)
    border_cross_air = models.BooleanField(default=False)
    id_made_no = models.BooleanField(default=False)
    id_made_real = models.BooleanField(default=False)
    id_made_fake = models.BooleanField(default=False)
    id_made_false_name = models.BooleanField(default=False)
    id_made_other_false = models.BooleanField(default=False)
    id_source_pb = models.CharField(max_length=126, null=True)
    id_kept_by_broker = models.CharField(max_length=126, null=True)
    permission_contact_pv = models.CharField(max_length=126, null=True)
    permission_contact_whats_app = models.CharField(max_length=126, null=True)
    permission_contact_facebook = models.CharField(max_length=126, null=True)
    permission_contact_phone = models.CharField(max_length=126, null=True)
    
    # Legal
    legal_action_taken = models.CharField(max_length=126, null=True)
    legal_action_taken_case_type = models.CharField(max_length=126, null=True)
    legal_action_taken_filed_against = models.CharField(max_length=126, null=True)
    legal_action_taken_staff_police_not_enough_info = models.BooleanField(default=False)
    legal_action_taken_staff_trafficker_ran = models.BooleanField(default=False)
    legal_action_taken_staff_trafficker_relative = models.BooleanField(default=False)
    legal_action_taken_staff_pv_afraid_reputation = models.BooleanField(default=False)
    legal_action_taken_staff_pv_afraid_safety = models.BooleanField(default=False)
    legal_action_taken_staff_pv_or_family_bribed = models.BooleanField(default=False)
    legal_action_taken_staff_pv_does_not_believe = models.BooleanField(default=False)
    legal_action_taken_staff_pv_threatened = models.BooleanField(default=False)
    legal_action_taken_staff_family_not_willing = models.BooleanField(default=False)
    date_visit_police_station = models.DateField('Date:',null=True)
    officer_name = models.CharField(max_length=126, null=True)
    police_station_took_statement = models.BooleanField(default=False)
    police_station_took_statement_privately = models.BooleanField(default=False)
    police_station_threats_prevented_statement = models.BooleanField(default=False)
    police_station_victim_name_given_to_media = models.BooleanField(default=False)
    police_station_gave_trafficker_access_to_pv = models.BooleanField(default=False)
    police_interact_disrespectful = models.BooleanField(default=False)
    police_interact_unprofessional = models.BooleanField(default=False)
    police_interact_resistant_to_fir = models.BooleanField(default=False)
    police_interact_none = models.BooleanField(default=False)
    victim_statement_certified = models.CharField(max_length=126, null=True)
    victim_statement_certified_date = models.DateField('Date:', null=True)
    police_do_not_believe_crime = models.BooleanField(default=False)
    police_say_not_enough_evidence = models.BooleanField(default=False)
    trafficker_ran_away = models.BooleanField(default=False)
    unable_to_locate_trafficker = models.BooleanField(default=False)
    pv_will_not_testify = models.BooleanField(default=False)
    delayed_waiting_for_other_traffickers = models.BooleanField(default=False)
    police_are_scared = models.BooleanField(default=False)
    suspect_corruption_or_bribes = models.BooleanField(default=False)
    pv_think_would_have_been_trafficked = models.CharField(max_length=126, null=True)
    exploitation_forced_prostitution_exp = models.BooleanField(default=False)
    exploitation_forced_prostitution_occ = models.BooleanField(default=False)
    exploitation_forced_prostitution_pb = models.CharField(max_length=126, null=True)
    exploitation_forced_prostitution_lb = models.CharField(max_length=126, null=True)
    exploitation_sexual_abuse_exp = models.BooleanField(default=False)
    exploitation_sexual_abuse_occ = models.BooleanField(default=False)
    exploitation_sexual_abuse_pb = models.CharField(max_length=126, null=True)
    exploitation_sexual_abuse_lb = models.CharField(max_length=126, null=True)
    exploitation_physical_abuse_exp = models.BooleanField(default=False)
    exploitation_physical_abuse_occ = models.BooleanField(default=False)
    exploitation_physical_abuse_pb = models.CharField(max_length=126, null=True)
    exploitation_physical_abuse_lb = models.CharField(max_length=126, null=True)
    exploitation_debt_bondage_exp = models.BooleanField(default=False)
    exploitation_debt_bondage_occ = models.BooleanField(default=False)
    exploitation_debt_bondage_pb = models.CharField(max_length=126, null=True)
    exploitation_debt_bondage_lb = models.CharField(max_length=126, null=True)
    exploitation_forced_labor_exp = models.BooleanField(default=False)
    exploitation_forced_labor_occ = models.BooleanField(default=False)
    exploitation_forced_labor_pb = models.CharField(max_length=126, null=True)
    exploitation_forced_labor_lb = models.CharField(max_length=126, null=True)
    exploitation_organ_removal_exp = models.BooleanField(default=False)
    exploitation_organ_removal_occ = models.BooleanField(default=False)
    exploitation_organ_removal_pb = models.CharField(max_length=126, null=True)
    exploitation_organ_removal_lb = models.CharField(max_length=126, null=True)
    exploitation_other_value = models.CharField(max_length=126, null=True)
    exploitation_other_exp = models.BooleanField(default=False)
    exploitation_other_occ = models.BooleanField(default=False)
    exploitation_other_pb = models.CharField(max_length=126, null=True)
    exploitation_other_lb = models.CharField(max_length=126, null=True)
    
    # Final
    reported_blue_flags = models.PositiveIntegerField(null=True, blank=True)
    total_blue_flags = models.PositiveIntegerField(null=True, blank=True)
    case_notes = models.TextField('Case Notes', blank=True)

    class Meta:
        abstract = True
    
    def get_key(self):
        return self.cif_number
    
    def get_form_type_name(self):
        return 'CIF'
    
    @staticmethod
    def key_field_name():
        return 'cif_number'


class PotentialVictimCore(BaseCard):
    person = models.ForeignKey(Person)
    social_media = models.CharField(max_length=1024, null=True)
    flag_count = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True

class TransporationCore(BaseCard):
    transportation_kind = models.CharField(max_length=126, null=True)
    transportation_order_number = models.PositiveIntegerField(null=True, blank=True)
    transportation_date  = models.DateField('Date:', null=True)
    transportation_crossing = models.CharField(max_length=126, null=True)
    flag_count = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True


class PersonBoxCore(BaseCard):
    pb_number = models.PositiveIntegerField(null=True, blank=True)
    person = models.ForeignKey(Person)
    case_filed_against = models.CharField(max_length=126, null=True)
    arrested = models.CharField(max_length=126, null=True)
    social_media = models.CharField(max_length=1024, null=True)
    role = models.CharField(max_length=126, null=True)
    relation_to_pv = models.CharField(max_length=126, null=True)
    appearance = models.CharField(max_length=126, null=True)
    occupation = models.CharField(max_length=126, null=True)
    definitely_trafficked_many = models.BooleanField(default=False)
    has_trafficked_some = models.BooleanField(default=False)
    suspected_trafficker = models.BooleanField(default=False)
    dont_believe_trafficker = models.BooleanField(default=False)
    pv_definitely_trafficked_many = models.BooleanField(default=False)
    pv_has_trafficked_some = models.BooleanField(default=False)
    pv_suspected_trafficker = models.BooleanField(default=False)
    pv_dont_believe_trafficker = models.BooleanField(default=False)
    associated_lb = models.CharField(max_length=126, null=True)
    flag_count = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True

class LocationBoxCore(BaseCard):
    lb_number = models.PositiveIntegerField(null=True, blank=True)
    place = models.CharField(max_length=126, null=True)
    place_kind = models.CharField(max_length=126, null=True)
    country = models.CharField(max_length=126, null=True)
    address2 = models.ForeignKey(Address2, null=True)
    phone = models.CharField(max_length=126, null=True)
    name_signboard = models.CharField(max_length=126, null=True)
    location_in_town = models.CharField(max_length=126, null=True)
    color = models.CharField(max_length=126, null=True)
    number_of_levels = models.CharField(max_length=126, null=True)
    person_in_charge = models.CharField(max_length=126, null=True)
    nearby_landmarks = models.CharField(max_length=126, null=True)
    pv_stayed_not_applicable = models.BooleanField(default=False)
    pv_stayed_days = models.PositiveIntegerField(null=True, blank=True)
    pv_stayed_start_date  = models.DateField('Date:', null=True)
    pv_attempt_hide_not_applicable = models.BooleanField(default=False)
    pv_attempt_hide_no = models.BooleanField(default=False)
    pv_attempt_hide_yes = models.BooleanField(default=False)
    pv_attempt_hide_explaination = models.CharField(max_length=126, null=True)
    pv_free_to_go_not_applicable = models.BooleanField(default=False)
    pv_free_to_go_yes = models.BooleanField(default=False)
    pv_free_to_go_no = models.BooleanField(default=False)
    pv_free_to_go_explaination = models.CharField(max_length=126, null=True)
    number_other_pvs_at_location = models.CharField(max_length=126, null=True)
    associated_pb = models.CharField(max_length=126, null=True)
    flag_count = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True

class VehicleBoxCore(BaseCard):
    vb_number = models.PositiveIntegerField(null=True, blank=True)
    license_plate = models.CharField(max_length=126, null=True)
    vehicle_type = models.CharField(max_length=126, null=True)
    description = models.CharField(max_length=126, null=True)
    associated_pb = models.CharField(max_length=126, null=True)
    flag_count = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        abstract = True

class CifAttachment(BaseCard):
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='cif_attachments')
    
    class Meta:
        abstract = True


