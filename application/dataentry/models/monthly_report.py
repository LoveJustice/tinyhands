from django.db import models

from .form import BaseForm, BaseCard

class MonthlyReport(BaseForm):
    # Top
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    
    # Governance
    govern_num_subcommittee_meetings= models.CharField(max_length=126, null=True)
    govern_num_sc_visits = models.CharField(max_length=126, null=True)
    govern_core_values = models.CharField(max_length=126, null=True)
    govern_coord_records = models.BooleanField(default=False)
    govern_coord_security = models.BooleanField(default=False)
    govern_coord_aftercare = models.BooleanField(default=False)
    govern_coord_paralegal = models.BooleanField(default=False)
    govern_coord_investigator = models.BooleanField(default=False)
    govern_coord_awareness = models.BooleanField(default=False)
    govern_coord_accounting = models.BooleanField(default=False)
    govern_coord_shelter = models.BooleanField(default=False)
    govern_signed = models.BooleanField(default=False)
    govern_signed_by = models.CharField(max_length=126, null=True)
    govern_points = models.PositiveIntegerField(default=0)
    
    # LOGISTICS & REGISTRATION
    logistics_progress_ngo = models.CharField(max_length=126, null=True)
    logistics_progress_cdo = models.CharField(max_length=126, null=True)
    logistics_progress_municipal_rural = models.CharField(max_length=126, null=True)
    logistics_progress_ward = models.CharField(max_length=126, null=True)
    logistics_progress_police = models.CharField(max_length=126, null=True)
    logistics_submit_local_law_enforcement = models.CharField(max_length=126, null=True)
    logistics_signed = models.BooleanField(default=False)
    logistics_signed_by = models.CharField(max_length=126, null=True)
    logistics_points = models.PositiveIntegerField(default=0)
    
    # HUMAN RESOURCES 
    human_staff_hours = models.CharField(max_length=126, null=True)
    human_appointment_and_contract = models.CharField(max_length=126, null=True)
    human_anti_corruption = models.CharField(max_length=126, null=True)
    human_information_to_national_office = models.CharField(max_length=126, null=True)
    human_percent_tms_exam = models.CharField(max_length=126, null=True)
    human_percent_coordinator_exam = models.CharField(max_length=126, null=True)
    human_signed = models.BooleanField(default=False)
    human_signed_by = models.CharField(max_length=126, null=True)
    human_points = models.PositiveIntegerField(default=0)
    
    # AWARENESS
    awareness_staff_hours = models.CharField(max_length=126, null=True)
    awareness_sc_hours = models.CharField(max_length=126, null=True)
    awareness_phone_calls = models.CharField(max_length=126, null=True)
    awareness_contact_cards = models.CharField(max_length=126, null=True)
    awareness_brochures = models.CharField(max_length=126, null=True)
    awareness_most_recent_awareness_gathering = models.CharField(max_length=126, null=True)
    awareness_most_recent_transport_gathering = models.CharField(max_length=126, null=True)
    awareness_signed = models.BooleanField(default=False)
    awareness_signed_by = models.CharField(max_length=126, null=True)
    awareness_points = models.PositiveIntegerField(default=0)
    
    # SECURITY
    security_protocol_followed = models.CharField(max_length=126, null=True)
    security_vary_routes = models.CharField(max_length=126, null=True)
    security_rotate_shifts = models.CharField(max_length=126, null=True)
    security_vary_clothing = models.CharField(max_length=126, null=True)
    security_threats_reported = models.CharField(max_length=126, null=True)
    security_protection_devices = models.CharField(max_length=126, null=True)
    security_signed = models.BooleanField(default=False)
    security_signed_by = models.CharField(max_length=126, null=True)
    security_points = models.PositiveIntegerField(default=0)
    
    # ACCOUNTING
    accounting_receipt = models.CharField(max_length=126, null=True)
    accounting_daybook = models.CharField(max_length=126, null=True)
    accounting_payment_record = models.CharField(max_length=126, null=True)
    accounting_submitted_yearly = models.CharField(max_length=126, null=True)
    accounting_signed = models.BooleanField(default=False)
    accounting_signed_by = models.CharField(max_length=126, null=True)
    accounting_points = models.PositiveIntegerField(default=0)
    
    # VICTIM ENGAGEMENT
    engagement_questioned = models.CharField(max_length=126, null=True)
    engagement_number_of_vdfs = models.PositiveIntegerField(default=0, null=True)
    engagement_intercept_poster = models.CharField(max_length=126, null=True)
    engagement_movement_poster = models.CharField(max_length=126, null=True)
    engagement_signed = models.BooleanField(default=False)
    engagement_signed_by = models.CharField(max_length=126, null=True)
    engagement_points = models.PositiveIntegerField(default=0)

    # RECORDS
    records_log_book = models.CharField(max_length=126, null=True)
    shelter_log_book = models.CharField(max_length=126, null=True)
    records_irf_fully_filled_out = models.CharField(max_length=126, null=True)
    records_photo_percent = models.CharField(max_length=126, null=True)
    records_verified_phone_percent = models.CharField(max_length=126, null=True)
    records_vdf_percent = models.CharField(max_length=126, null=True)
    records_signed = models.BooleanField(default=False)
    records_signed_by = models.CharField(max_length=126, null=True)
    records_points = models.PositiveIntegerField(default=0)

    # AFTERCARE
    aftercare_eduction_chori = models.CharField(max_length=126, null=True)
    aftercare_eduction_dhuwani = models.CharField(max_length=126, null=True)
    aftercare_eduction_tdmgd = models.CharField(max_length=126, null=True)
    aftercare_eduction_nepalese_homes = models.CharField(max_length=126, null=True)
    aftercare_eduction_top_women_jobs = models.CharField(max_length=126, null=True)
    aftercare_eduction_mtv_exit = models.CharField(max_length=126, null=True)
    aftercare_eduction_touch = models.CharField(max_length=126, null=True)
    aftercare_tracts = models.CharField(max_length=126, null=True)
    aftercare_bibles = models.CharField(max_length=126, null=True)
    aftercare_messagebook = models.CharField(max_length=126, null=True)
    aftercare_film = models.CharField(max_length=126, null=True)
    aftercare_only_female_staff_in_shelter = models.CharField(max_length=126, null=True)
    aftercare_always_1_staff_in_shelter = models.CharField(max_length=126, null=True)
    aftercare_victims_tested_std = models.CharField(max_length=126, null=True)
    aftercare_interview_recorded = models.CharField(max_length=126, null=True)
    aftercare_interview_private = models.CharField(max_length=126, null=True)
    aftercare_interview_only_staff_sc_police = models.CharField(max_length=126, null=True)
    aftercare_follow_up = models.CharField(max_length=126, null=True)
    aftercare_signed = models.BooleanField(default=False)
    aftercare_signed_by = models.CharField(max_length=126, null=True)
    aftercare_points = models.PositiveIntegerField(default=0)
    
    # PARALEGAL
    paralegal_total_cases = models.CharField(max_length=126, null=True)
    paralegal_set_to_national_office = models.CharField(max_length=126, null=True)
    paralegal_num_cifs_to_national_office = models.PositiveIntegerField(null=True)
    paralegal_percent_cif_clear_envidence_cases = models.CharField(max_length=126, null=True)  # moved to records
    paralegal_active_case_update_to_nation_office = models.CharField(max_length=126, null=True)
    paralegal_arrests_last_month = models.PositiveIntegerField(default=0, null=True)
    paralegal_gd_last_month = models.PositiveIntegerField(default=0, null=True)
    paralegal_when_to_file_case_poster = models.CharField(max_length=126, null=True)
    paralegal_legal_advisor_appointed = models.CharField(max_length=126, null=True)
    paralegal_signed = models.BooleanField(default=False)
    paralegal_signed_by = models.CharField(max_length=126, null=True)
    paralegal_points = models.PositiveIntegerField(default=0)

    # INVESTIGATIONS 
    investigations_num_hvc = models.CharField(max_length=126, null=True)
    investigations_int_from_hvc = models.CharField(max_length=126, null=True)
    investigations_hotels_visited = models.CharField(max_length=126, null=True)
    investigations_signed = models.BooleanField(default=False)
    investigations_signed_by = models.CharField(max_length=126, null=True)
    investigations_points = models.PositiveIntegerField(default=0)

    # Final
    notes = models.TextField(blank=True)
    final_signed = models.BooleanField(default=False)
    final_signed_by = models.CharField(max_length=126, null=True)
    average_points = models.FloatField(default=0)
    
    class Meta:
        unique_together = ("station", "year", "month")
    
    def get_key(self):
        if self.id:
            return str(self.id)
        else:
            # Return None instead of str(None) aka 'None' so we don't try to pull an Incident on serialize_form
            return None
    
    def get_form_type_name(self):
        return 'MONTHLY_REPORT'
    
    @staticmethod
    def key_field_name():
        return 'id'

class MonthlyReportAttachment(BaseCard):
    monthly_report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE)
    attachment_number = models.PositiveIntegerField(null=True, blank=True)
    description = models.CharField(max_length=126, null=True)
    attachment = models.FileField('Attach scanned copy of form (pdf or image)', upload_to='mrf_attachments')
    private_card = models.BooleanField(default=True)
    option = models.CharField(max_length=126, null=True)
    
    def is_private(self):
        return self.private_card

    def set_parent(self, the_parent):
        self.monthly_report = the_parent

