import csv
import io
import math

from django.db.models import Q
from django.conf import settings

from dataentry.models import Country, IntercepteeCommon, IrfCommon, VdfCommon

class ExportFormCsv:
    def __init__(self, country_list, start_date, end_date, status, remove_pi, sample):
        self.country_list = country_list
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.remove_pi = remove_pi
        self.sample = sample
    
    def station_headers(self):
        if self.remove_pi:
            return ['country']
        else:
            return ['country', 'station_name']
    
    def station_export(self, station):
        if self.remove_pi:
            return [station.operating_country.name]
        else:
            return [station.operating_country.name, station.station_name]


class IrfCsv (ExportFormCsv):
    def __init__(self, country_list, start_date, end_date, status, remove_pi, sample, remove_suspects, minimum_red_flags, include_case_notes):
        super().__init__(country_list, start_date, end_date, status, remove_pi, sample)
        self.remove_suspects = remove_suspects
        self.minimum_red_flags = minimum_red_flags
        self.include_case_notes = include_case_notes
        self.person_columns = [
                "role",
                "full_name",
                "gender",
                "age",
                "birthdate",
                "address",
                "latitude",
                "longitude",
                "nationality",
                "phone_contact"
            ]
        self.person_private = [
                "full_name",
                "birthdate",
                "address",
                "latitude",
                "longitude",
                "phone_contact"
            ]
        self.export_columns = [
            "status",
            "irf_number",
            "date_of_interception",
            "time_of_interception",
            "number_of_victims",
            "number_of_traffickers",
            "location",
            "staff_name",
            "profile",
            "where_going_destination",
            "industry",
            "vulnerability_afraid_of_host",
            "vulnerability_connection_host_unclear",
            "vulnerability_doesnt_have_required_visa",
            "vulnerability_doesnt_speak_destination_language",
            "vulnerability_doesnt_speak_english",
            "vulnerability_family_friend_arranged_travel",
            "vulnerability_family_unwilling",
            "vulnerability_first_time_traveling_abroad",
            "vulnerability_group_facebook",
            "vulnerability_group_missed_call",
            "vulnerability_group_never_met_before",
            "vulnerability_group_other_website",
            "vulnerability_insufficient_resource",
            "vulnerability_met_on_the_way",
            "vulnerability_minor_without_guardian",
            "vulnerability_non_relative_paid_flight",
            "vulnerability_paid_flight_in_cash",
            "vulnerability_person_speaking_on_their_behalf",
            "vulnerability_refuses_family_info",
            "vulnerability_supporting_documents_one_way_ticket",
            "vulnerability_under_18_family_doesnt_know",
            "vulnerability_where_going_doesnt_know",
            "evade_appearance_avoid_officials",
            "evade_caught_in_lie",
            "evade_couldnt_confirm_job",
            "evade_job_details_changed_en_route",
            "evade_no_bags_long_trip",
            "evade_noticed_carrying_full_bags",
            "evade_signs_confirmed_deception",
            "evade_signs_fake_documentation",
            "evade_signs_forged_false_documentation",
            "evade_signs_other",
            "evade_signs_treatment",
            "evade_study_doesnt_know_school_details",
            "evade_visa_misuse",
            "evidence_categorization",
            "control_connected_known_trafficker",
            "control_contradiction_stories",
            "control_drugged_or_drowsy",
            "control_job",
            "control_job_underqualified",
            "control_led_other_country",
            "control_less_than_2_weeks_before_eloping",
            "control_married_in_past_2_8_weeks",
            "control_married_in_past_2_weeks",
            "control_mobile_phone_taken_away",
            "control_no_address_phone",
            "control_normal_pay",
            "control_not_real_job",
            "control_owes_debt",
            "control_passport_with_broker",
            "control_promised_double",
            "control_promised_higher",
            "control_promised_pay",
            "control_relationship_to_get_married",
            "control_reported_total_red_flags",
            "control_status_known_trafficker",
            "control_traveling_because_of_threat",
            "control_traveling_with_someone_not_with_them",
            "control_under_18_family_unwilling",
            "control_where_going_someone_paid_expenses",
            "control_wife_under_18",
            "computed_total_red_flags",
            "immigration_exit",
            "immigration_lj_entry",
            "immigration_lj_exit",
            "immigration_lj_transit",
            "talked_to_family_member",
            "immigration_entry",
            "immigration_transit",
            "immigration_case_number",
            "who_noticed",
            "which_contact",
            "contact_paid",
            "contact_paid_how_much",
            "staff_who_noticed",
            "reason_for_intercept",
            "flight_number",
            "how_sure_was_trafficking",
            "convinced_by_staff",
            "convinced_by_family",
            "convinced_family_phone",
            "convinced_by_police",
            "pv_stopped_on_own",
            "rescue",
            "verified_evidence_categorization",
            "verified_date"
        ]
        
        self.private = [
            "convinced_by_family",
            "convinced_family_phone",
            "flight_number",
            "full_name",
            "immigration_case_number",
            "immigration_entry",
            "immigration_transit",
            "reason_for_intercept",
            "rescue",
            "staff_name",
            "staff_who_noticed",
            "talked_to_family_member",
            "time_of_interception",
            "which_contact",
            "who_noticed",
            ]
    
    def headers(self):
        headers = self.station_headers()
        for header in self.export_columns:
            if self.remove_pi:
                if header not in self.private:
                    headers.append(header)
            else:
                headers.append(header)
        headers = headers + self.interceptee_headers()
        if self.include_case_notes and not self.remove_pi:
            headers.append('case_notes')
        return headers
    
    def interceptee_headers(self):
        headers = []
        for header in self.person_columns:
            if self.remove_pi:
                if header not in self.person_private:
                    headers.append(header)
            else:
                headers.append(header)
        headers.append("not_physically_present")
        return headers
    
    def interceptee(self, interceptee):
        row = []
        for column in self.person_columns:
            if self.remove_pi:
                if column not in self.person_private:
                    row.append(getattr(interceptee.person, column, None))
            else:
                row.append(getattr(interceptee.person, column, None))
        row.append(getattr(interceptee, "not_physically_present", None))
        return row
    
    def perform_export(self):
        interceptees = IntercepteeCommon.objects.filter(
            interception_record__station__operating_country__in = self.country_list,
            interception_record__verified_date__gte=self.start_date,
            interception_record__verified_date__lte=self.end_date)
        if self.status is not None:
            if self.status == 'evidence':
                interceptees = interceptees.filter(interception_record__verified_evidence_categorization='Evidence of Trafficking')
            elif self.status == 'high_risk':
                interceptees = interceptees.filter(interception_record__verified_evidence_categorization='High Risk of Trafficking')
            elif self.status == 'counted_intercept':
                interceptees = interceptees.filter(Q(interception_record__verified_evidence_categorization='Evidence of Trafficking') |
                                   Q(interception_record__verified_evidence_categorization='High Risk of Trafficking'))
        if self.remove_suspects:
            interceptees = interceptees.filter(person__role='PVOT')
        if self.minimum_red_flags > 0:
            interceptees = interceptees.filter(interception_record__computed_total_red_flags__gte=self.minimum_red_flags)
        
        interceptees = interceptees.order_by('interception_record__id', 'id')
        
        if len(self.country_list) > 1:
            export_name = 'all'
        else:
            export_name = self.country_list[0].name
        
        export_name += '_IRFS_' + str(self.start_date) + '_to_' + str(self.end_date) + '_' + self.status + '_forms'
        if self.remove_pi:
            export_name += '(without PIs)'
        
        rate = self.sample / 100.0
        
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(self.headers())
        
        processed = 0
        exported = 0
        for interceptee in interceptees:
            processed += 1
            if processed * rate < exported:
                continue
            
            row = self.station_export(interceptee.interception_record.station)
            for column in self.export_columns:
                if self.remove_pi:
                    if column not in self.private:
                        row.append(getattr(interceptee.interception_record, column, None))
                else:
                    row.append(getattr(interceptee.interception_record, column, None))
            row += self.interceptee(interceptee)
            if self.include_case_notes:
                row.append(getattr(interceptee.interception_record,'case_notes', None))
            
            writer.writerow(row)
            exported += 1
        
        csv_file.seek(0)
        return {'name': export_name + '.csv', 'file': csv_file}

class PvfCsv (ExportFormCsv):
    
    def __init__(self, country_list, start_date, end_date, status, remove_pi, sample, include_verification_category, follow_up):
        super().__init__(country_list, start_date, end_date, status, remove_pi, sample)
        self.include_verification_category = include_verification_category
        self.follow_up = follow_up
        
        self.person_columns = [
            "full_name",
            "gender",
            "age",
            "phone_contact",
            "birthdate",
            "social_media",
            "nationality",
            "occupation",
            "guardian_name",
            "guardian_phone",
        ]
        self.person_private = [
            "full_name",
            "birthdate",
            "guardian_name",
            "guardian_phone",
            "phone_contact",
            "social_media",
        ]
        self.export_columns = [
            "vdf_number",
            "staff_name",
            "interview_date",
            "location",
            "guardian_know_destination",
            "family_guardian_pressure",
            "try_to_send_overseas_again",
            "feel_safe_with_guardian",
            "do_you_want_to_go_home",
            "sexual_abuse",
            "physical_abuse",
            "emotional_abuse",
            "guardian_drink_alcohol",
            "guardian_use_drugs",
            "family_economic_situation",
            "express_suicidal_thoughts",
            "is_evidence_that_guardians_sold",
            "evidence_that_guardians_sold",
            "total_situational_alarms",
            "station_recommendation_for_victim",
            "why_sent_home_with_with_alarms",
            "awareness_of_exploitation_before_interception",
            "victim_heard_message_before",
            "what_victim_believes_now",
            "staff_share_gospel",
            "share_gospel_film",
            "share_gospel_tract",
            "share_gospel_oral",
            "share_gospel_testimony",
            "share_gospel_book",
            "share_gospel_other",
            "date_victim_left",
            "how_pv_released",
            "service_education_about_ht",
            "service_food",
            "service_legal_support",
            "service_medical_support",
            "service_safe_foreign_employment",
            "service_safe_foreign_employment",
            "service_travel_support",
            "country_pv_sent",
            "pv_spent_time_at_shelter",
            "someone_pick_up_victim",
            "who_victim_released",
            "who_victim_released_name",
            "who_victim_released_phone",
            "where_victim_sent",
            "where_victim_sent_details",
            "fundraising_purpose",
            "consent_to_use_information",
            "victim_signature",
            "guardian_signature",
            "case_notes",
            "logbook_submitted",
        ]
            
        self.private = [
            "case_notes",
            "evidence_that_guardians_sold",
            "staff_name",
            "who_victim_released_name",
            "who_victim_released_phone",
            "why_sent_home_with_with_alarms",
        ]
    
    def headers(self):
        headers = self.station_headers() + self.person_headers()
        for header in self.export_columns:
            if self.remove_pi:
                if header not in self.private:
                    headers.append(header)
            else:
                headers.append(header)
        if self.include_verification_category:
            headers.append('verified_evidence_categorization')
        return headers
    
    def person_headers(self):
        headers = []
        for header in self.person_columns:
            if self.remove_pi:
                if header not in self.person_private:
                    headers.append(header)
            else:
                headers.append(header)
        return headers
    
    def person(self, personObject):
        row = []
        for column in self.person_columns:
            if self.remove_pi:
                if column not in self.person_private:
                    row.append(getattr(personObject, column, None))
            else:
                row.append(getattr(personObject, column, None))
        return row
    
    def export_rows(self, writer, pvfs, rate):
        processed = 0
        exported = 0
        for pvf in pvfs:
            processed += 1
            if processed * rate < exported:
                continue
            
            row = self.station_export(pvf.station) + self.person(pvf.victim)
            for column in self.export_columns:
                if self.remove_pi:
                    if column not in self.private:
                        row.append(getattr(pvf, column, None))
                else:
                    row.append(getattr(pvf, column, None))
            
            if self.include_verification_category:
                for char_index in reversed(range(len(pvf.vdf_number))):
                    if pvf.vdf_number[char_index] >= '0' and pvf.vdf_number[char_index] <= '9':
                        irf_number = pvf.vdf_number[0:char_index+1]
                        try:
                            irf = IrfCommon.objects.get(irf_number=irf_number)
                            row.append(irf.verified_evidence_categorization)
                            break
                        except:
                            row.append('')
                
            
            writer.writerow(row)
            exported += 1
    
    def check_contact(self, value):
        return value is not None and len(value) > 0 and value != '-' and value.lower() != 'n/a' and value.lower() != 'na'
    
    def perform_export(self):
        pvfs = VdfCommon.objects.filter(
            station__operating_country__in = self.country_list,
            logbook_submitted__gte=self.start_date,
            logbook_submitted__lte=self.end_date)
        
        if self.status is not None and self.status == 'approved':
                pvfs.filter(status='approved')
        
        if len(self.country_list) > 1:
            export_name = 'all'
        else:
            export_name = self.country_list[0].name
        
        export_name += '_PVFS_' + str(self.start_date) + '_to_' + str(self.end_date) + '_' + self.status + '_forms'
        if self.remove_pi:
            export_name += '(without PIs)'
        if self.follow_up:
            export_name += '_Gospel Sample'
            follow_up_pvfs = pvfs.filter(what_victim_believes_now='Came to believe that Jesus is the one true God')
            other_pvfs = pvfs.exclude(what_victim_believes_now='Came to believe that Jesus is the one true God')
            desired_sample = math.ceil(len(pvfs) * self.sample / 100.0)
            # Include PVFs with phone number or guardian phone number before those without
            follow_ups_with_contact = []
            follow_ups_without_contact = []
            for pvf in follow_up_pvfs:
                if self.check_contact(pvf.victim.phone_contact) or self.check_contact(pvf.victim.guardian_phone):
                    follow_ups_with_contact.append(pvf)
                else:
                    follow_ups_without_contact.append(pvf)
            
            follow_up_pvfs = follow_ups_with_contact + follow_ups_without_contact
            if len(follow_up_pvfs) > desired_sample:
                rate = 0
            else:
                desired_sample -= len(follow_up_pvfs)
                rate = desired_sample * 1.0 / len(other_pvfs)
        else:
            follow_up_pvfs = []
            other_pvfs = pvfs
            rate = self.sample / 100.0
        
        csv_file = io.StringIO()
        
        writer = csv.writer(csv_file)
        writer.writerow(self.headers())
        if len(follow_up_pvfs) > 0:
            # include all
            self.export_rows(writer, follow_up_pvfs, 2.0)
        if rate > 0:
            self.export_rows(writer, other_pvfs, rate)
        
        csv_file.seek(0)
        return {'name': export_name + '.csv', 'file': csv_file}
                
        