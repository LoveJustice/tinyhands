# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VictimInterview.abuse_happened_denied_food'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_denied_food')

        # Deleting field 'VictimInterview.migration_plans_arranged_marriage'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_arranged_marriage')

        # Deleting field 'VictimInterview.victim_where_going_region'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_region')

        # Deleting field 'VictimInterview.victim_how_met_broker_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_other_value')

        # Deleting field 'VictimInterview.primary_motivation_tour_travel'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_tour_travel')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value')

        # Deleting field 'VictimInterview.passport_made_no_passport_made'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_no_passport_made')

        # Deleting field 'VictimInterview.migration_plans_job_other'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_other')

        # Deleting field 'VictimInterview.reason_no_legal_family_afraid_reputation'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_family_afraid_reputation')

        # Deleting field 'VictimInterview.primary_motivation_other_value'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_other_value')

        # Deleting field 'VictimInterview.migration_plans_job_factory'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_factory')

        # Deleting field 'VictimInterview.reason_no_legal_victims_own_people'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_victims_own_people')

        # Deleting field 'VictimInterview.migration_plans_education'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_education')

        # Deleting field 'VictimInterview.victim_where_going_other_gulf_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_other_gulf_value')

        # Deleting field 'VictimInterview.primary_motivation_personal_debt'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_personal_debt')

        # Deleting field 'VictimInterview.primary_motivation_get_an_education'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_get_an_education')

        # Deleting field 'VictimInterview.victim_lives_with_other_relative'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_other_relative')

        # Deleting field 'VictimInterview.reason_no_legal_victim_family_bribed'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_victim_family_bribed')

        # Deleting field 'VictimInterview.abuse_happened_threats'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_threats')

        # Deleting field 'VictimInterview.migration_plans_job_shop'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_shop')

        # Deleting field 'VictimInterview.migration_plans_job_laborer'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_laborer')

        # Deleting field 'VictimInterview.migration_plans_job_baby_care'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_baby_care')

        # Deleting field 'VictimInterview.passport_made_false_info'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_false_info')

        # Deleting field 'VictimInterview.primary_motivation_support_family'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_support_family')

        # Deleting field 'VictimInterview.migration_plans_eloping'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_eloping')

        # Deleting field 'VictimInterview.abuse_happened_sexual_harassment'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_sexual_harassment')

        # Deleting field 'VictimInterview.migration_plans_medical_treatment'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_medical_treatment')

        # Deleting field 'VictimInterview.migration_plans_job_value'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_value')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other_value')

        # Deleting field 'VictimInterview.passport_made_was_fake'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_was_fake')

        # Deleting field 'VictimInterview.reason_no_legal_ran_away'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_ran_away')

        # Deleting field 'VictimInterview.primary_motivation_bad_home_marriage'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_bad_home_marriage')

        # Deleting field 'VictimInterview.reason_no_legal_police_bribed'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_police_bribed')

        # Deleting field 'VictimInterview.victim_lives_with_own_parents'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_own_parents')

        # Deleting field 'VictimInterview.primary_motivation_family_debt'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_family_debt')

        # Deleting field 'VictimInterview.migration_plans_shopping'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_shopping')

        # Deleting field 'VictimInterview.victim_lives_with_husbands_family'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_husbands_family')

        # Deleting field 'VictimInterview.reason_no_legal_other'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_other')

        # Deleting field 'VictimInterview.victim_lives_with_husband'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_husband')

        # Deleting field 'VictimInterview.abuse_happened_forced_drugs'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_forced_drugs')

        # Deleting field 'VictimInterview.migration_plans_other'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_other')

        # Deleting field 'VictimInterview.migration_plans_visit_brokers_home'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_visit_brokers_home')

        # Deleting field 'VictimInterview.primary_motivation_love_marriage'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_love_marriage')

        # Deleting field 'VictimInterview.reason_no_legal_interference_by_powerful_people'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_interference_by_powerful_people')

        # Deleting field 'VictimInterview.primary_motivation_other'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_other')

        # Deleting field 'VictimInterview.reason_no_legal_victim_afraid_reputation'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_victim_afraid_reputation')

        # Deleting field 'VictimInterview.migration_plans_job_brothel'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_brothel')

        # Deleting field 'VictimInterview.reason_no_legal_no_trafficking_suspected'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_no_trafficking_suspected')

        # Deleting field 'VictimInterview.reason_no_legal_victim_afraid_safety'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_victim_afraid_safety')

        # Deleting field 'VictimInterview.migration_plans_job_household'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_household')

        # Deleting field 'VictimInterview.migration_plans_other_value'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_other_value')

        # Deleting field 'VictimInterview.passport_made_real_passport_made'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_real_passport_made')

        # Deleting field 'VictimInterview.reason_no_legal_family_afraid_safety'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_family_afraid_safety')

        # Deleting field 'VictimInterview.migration_plans_travel_tour'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_travel_tour')

        # Deleting field 'VictimInterview.primary_motivation_support_myself'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_support_myself')

        # Deleting field 'VictimInterview.passport_made_false_name'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_false_name')

        # Deleting field 'VictimInterview.victim_caste_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_caste_other_value')

        # Deleting field 'VictimInterview.reason_no_legal_girl_going_herself'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_girl_going_herself')

        # Deleting field 'VictimInterview.victim_lives_with_alone'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_alone')

        # Deleting field 'VictimInterview.abuse_happened_sexual_abuse'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_sexual_abuse')

        # Deleting field 'VictimInterview.primary_motivation_didnt_know'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_didnt_know')

        # Deleting field 'VictimInterview.migration_plans_job_broker_did_not_say'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_broker_did_not_say')

        # Deleting field 'VictimInterview.victim_where_going_other_india_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_other_india_value')

        # Deleting field 'VictimInterview.victim_lives_with_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_other_value')

        # Deleting field 'VictimInterview.victim_occupation_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_occupation_other_value')

        # Deleting field 'VictimInterview.abuse_happened_physical_abuse'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_physical_abuse')

        # Deleting field 'VictimInterview.migration_plans_job_hotel'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_job_hotel')

        # Deleting field 'VictimInterview.migration_plans_meet_own_family'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_meet_own_family')

        # Deleting field 'VictimInterview.victim_lives_with_friends'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_friends')

        # Deleting field 'VictimInterview.reason_no_legal_not_enough_info'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_not_enough_info')

        # Deleting field 'VictimInterview.victim_lives_with_other'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with_other')

        # Adding field 'VictimInterview.victim_lives_with'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans'
        db.add_column(u'dataentry_victiminterview', 'migration_plans',
                      self.gf('django.db.models.fields.CharField')(default='test', max_length=255),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_second'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_second',
                      self.gf('django.db.models.fields.BooleanField')(default='test', max_length=255),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation',
                      self.gf('django.db.models.fields.CharField')(default='test', max_length=255),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made'
        db.add_column(u'dataentry_victiminterview', 'passport_made',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.reason_no_legal'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal',
                      self.gf('django.db.models.fields.CharField')(default='test', max_length=255),
                      keep_default=False)

        # Adding field 'VictimInterview.reason_no_legal_interference_value'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_interference_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.scanned_form'
        db.add_column(u'dataentry_victiminterview', 'scanned_form',
                      self.gf('django.db.models.fields.files.FileField')(default='', max_length=100, blank=True),
                      keep_default=False)


        # Changing field 'VictimInterview.victim_guardian_uses_drugs'
        db.alter_column(u'dataentry_victiminterview', 'victim_guardian_uses_drugs', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.legal_action_against_traffickers'
        db.alter_column(u'dataentry_victiminterview', 'legal_action_against_traffickers', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_parents_marital_status'
        db.alter_column(u'dataentry_victiminterview', 'victim_parents_marital_status', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_caste'
        db.alter_column(u'dataentry_victiminterview', 'victim_caste', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.interviewer_recommendation'
        db.alter_column(u'dataentry_victiminterview', 'interviewer_recommendation', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_family_economic_situation'
        db.alter_column(u'dataentry_victiminterview', 'victim_family_economic_situation', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_occupation'
        db.alter_column(u'dataentry_victiminterview', 'victim_occupation', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_primary_guardian'
        db.alter_column(u'dataentry_victiminterview', 'victim_primary_guardian', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_guardian_drinks_alcohol'
        db.alter_column(u'dataentry_victiminterview', 'victim_guardian_drinks_alcohol', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_home_had_emotional_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_emotional_abuse', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.manpower_involved'
        db.alter_column(u'dataentry_victiminterview', 'manpower_involved', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'VictimInterview.victim_home_had_physical_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_physical_abuse', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_education_level'
        db.alter_column(u'dataentry_victiminterview', 'victim_education_level', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'VictimInterview.victim_home_had_sexual_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_sexual_abuse', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Deleting field 'VictimInterviewPersonBox.who_is_this_coworker_of'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_coworker_of')

        # Deleting field 'VictimInterviewPersonBox.victim_believes_has_trafficked_some_girls'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_has_trafficked_some_girls')

        # Deleting field 'VictimInterviewPersonBox.interviewer_believes_has_trafficked_many_girls'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_has_trafficked_many_girls')

        # Deleting field 'VictimInterviewPersonBox.victim_believes_has_trafficked_many_girls'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_has_trafficked_many_girls')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_known_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_known_trafficker')

        # Deleting field 'VictimInterviewPersonBox.victim_believes_is_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_is_trafficker')

        # Deleting field 'VictimInterviewPersonBox.interviewer_believes_is_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_is_trafficker')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_boss_of'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_boss_of')

        # Deleting field 'VictimInterviewPersonBox.interviewer_believes_has_trafficked_some_girls'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_has_trafficked_some_girls')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_india_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_india_trafficker')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_passport'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_passport')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_manpower'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_manpower')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_broker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_broker')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_own_relative_of'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_own_relative_of')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_sex_industry'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_sex_industry')

        # Deleting field 'VictimInterviewPersonBox.victim_believes_is_not_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_is_not_trafficker')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_companion'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_companion')

        # Deleting field 'VictimInterviewPersonBox.interviewer_believes_is_not_trafficker'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_is_not_trafficker')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_contact_of_husband'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_contact_of_husband')

        # Adding field 'VictimInterviewPersonBox.who_is_this_relationship'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_relationship',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_role'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_role',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.interviewer_believes'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.victim_believes'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'victim_believes',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


        # Changing field 'VictimInterviewPersonBox.occupation'
        db.alter_column(u'dataentry_victiminterviewpersonbox', 'occupation', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):
        # Adding field 'VictimInterview.abuse_happened_denied_food'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_denied_food',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_arranged_marriage'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_arranged_marriage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.victim_where_going_region'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.victim_where_going_region' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.victim_where_going_region'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_region',
                      self.gf('django.db.models.fields.CharField')(max_length=255),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_tour_travel'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_tour_travel',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_no_passport_made'
        db.add_column(u'dataentry_victiminterview', 'passport_made_no_passport_made',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_other'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_family_afraid_reputation'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_family_afraid_reputation' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_family_afraid_reputation'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_family_afraid_reputation',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_other_value'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_factory'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_factory',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_victims_own_people'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_victims_own_people' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_victims_own_people'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_victims_own_people',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_education'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_education',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_other_gulf_value'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_other_gulf_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_personal_debt'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_personal_debt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_get_an_education'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_get_an_education',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_other_relative'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_other_relative',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_victim_family_bribed'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_victim_family_bribed' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_victim_family_bribed'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_victim_family_bribed',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_threats'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_threats',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_shop'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_shop',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_laborer'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_laborer',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_baby_care'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_baby_care',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_false_info'
        db.add_column(u'dataentry_victiminterview', 'passport_made_false_info',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_support_family'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_support_family',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_eloping'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_eloping',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_sexual_harassment'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_sexual_harassment',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_medical_treatment'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_medical_treatment',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_value'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_was_fake'
        db.add_column(u'dataentry_victiminterview', 'passport_made_was_fake',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_ran_away'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_ran_away' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_ran_away'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_ran_away',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_bad_home_marriage'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_bad_home_marriage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_police_bribed'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_police_bribed' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_police_bribed'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_police_bribed',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_own_parents'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_own_parents',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_family_debt'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_family_debt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_shopping'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_shopping',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_husbands_family'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_husbands_family',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_other'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_other' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_other'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_other',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_husband'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_husband',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_forced_drugs'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_forced_drugs',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_other'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_visit_brokers_home'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_visit_brokers_home',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_love_marriage'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_love_marriage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_interference_by_powerful_people'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_interference_by_powerful_people' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_interference_by_powerful_people'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_interference_by_powerful_people',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_other'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_victim_afraid_reputation'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_victim_afraid_reputation' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_victim_afraid_reputation'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_victim_afraid_reputation',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_brothel'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_brothel',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_no_trafficking_suspected'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_no_trafficking_suspected' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_no_trafficking_suspected'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_no_trafficking_suspected',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_victim_afraid_safety'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_victim_afraid_safety' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_victim_afraid_safety'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_victim_afraid_safety',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_household'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_household',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_other_value'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_real_passport_made'
        db.add_column(u'dataentry_victiminterview', 'passport_made_real_passport_made',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_family_afraid_safety'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_family_afraid_safety' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_family_afraid_safety'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_family_afraid_safety',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_travel_tour'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_travel_tour',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_support_myself'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_support_myself',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_false_name'
        db.add_column(u'dataentry_victiminterview', 'passport_made_false_name',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_caste_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_caste_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_girl_going_herself'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_girl_going_herself' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_girl_going_herself'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_girl_going_herself',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_alone'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_alone',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_sexual_abuse'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_sexual_abuse',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_didnt_know'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_didnt_know',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_broker_did_not_say'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_broker_did_not_say',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_other_india_value'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_other_india_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_occupation_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_occupation_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_physical_abuse'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_physical_abuse',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_job_hotel'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_job_hotel',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.migration_plans_meet_own_family'
        db.add_column(u'dataentry_victiminterview', 'migration_plans_meet_own_family',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_friends'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_friends',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'VictimInterview.reason_no_legal_not_enough_info'
        raise RuntimeError("Cannot reverse this migration. 'VictimInterview.reason_no_legal_not_enough_info' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'VictimInterview.reason_no_legal_not_enough_info'
        db.add_column(u'dataentry_victiminterview', 'reason_no_legal_not_enough_info',
                      self.gf('django.db.models.fields.BooleanField')(),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_lives_with_other'
        db.add_column(u'dataentry_victiminterview', 'victim_lives_with_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'VictimInterview.victim_lives_with'
        db.delete_column(u'dataentry_victiminterview', 'victim_lives_with')

        # Deleting field 'VictimInterview.migration_plans'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans')

        # Deleting field 'VictimInterview.migration_plans_second'
        db.delete_column(u'dataentry_victiminterview', 'migration_plans_second')

        # Deleting field 'VictimInterview.primary_motivation'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation')

        # Deleting field 'VictimInterview.passport_made'
        db.delete_column(u'dataentry_victiminterview', 'passport_made')

        # Deleting field 'VictimInterview.abuse_happened'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened')

        # Deleting field 'VictimInterview.reason_no_legal'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal')

        # Deleting field 'VictimInterview.reason_no_legal_interference_value'
        db.delete_column(u'dataentry_victiminterview', 'reason_no_legal_interference_value')

        # Deleting field 'VictimInterview.scanned_form'
        db.delete_column(u'dataentry_victiminterview', 'scanned_form')


        # Changing field 'VictimInterview.victim_guardian_uses_drugs'
        db.alter_column(u'dataentry_victiminterview', 'victim_guardian_uses_drugs', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.legal_action_against_traffickers'
        db.alter_column(u'dataentry_victiminterview', 'legal_action_against_traffickers', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.victim_parents_marital_status'
        db.alter_column(u'dataentry_victiminterview', 'victim_parents_marital_status', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'VictimInterview.victim_caste'
        db.alter_column(u'dataentry_victiminterview', 'victim_caste', self.gf('django.db.models.fields.CharField')(max_length=30))

        # Changing field 'VictimInterview.interviewer_recommendation'
        db.alter_column(u'dataentry_victiminterview', 'interviewer_recommendation', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.victim_family_economic_situation'
        db.alter_column(u'dataentry_victiminterview', 'victim_family_economic_situation', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.victim_occupation'
        db.alter_column(u'dataentry_victiminterview', 'victim_occupation', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'VictimInterview.victim_primary_guardian'
        db.alter_column(u'dataentry_victiminterview', 'victim_primary_guardian', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'VictimInterview.victim_guardian_drinks_alcohol'
        db.alter_column(u'dataentry_victiminterview', 'victim_guardian_drinks_alcohol', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.victim_home_had_emotional_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_emotional_abuse', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.manpower_involved'
        db.alter_column(u'dataentry_victiminterview', 'manpower_involved', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'VictimInterview.victim_home_had_physical_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_physical_abuse', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'VictimInterview.victim_education_level'
        db.alter_column(u'dataentry_victiminterview', 'victim_education_level', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'VictimInterview.victim_home_had_sexual_abuse'
        db.alter_column(u'dataentry_victiminterview', 'victim_home_had_sexual_abuse', self.gf('django.db.models.fields.CharField')(max_length=40))
        # Adding field 'VictimInterviewPersonBox.who_is_this_coworker_of'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_coworker_of',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.victim_believes_has_trafficked_some_girls'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_has_trafficked_some_girls',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.interviewer_believes_has_trafficked_many_girls'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_has_trafficked_many_girls',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.victim_believes_has_trafficked_many_girls'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_has_trafficked_many_girls',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_known_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_known_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.victim_believes_is_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_is_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.interviewer_believes_is_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_is_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_boss_of'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_boss_of',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.interviewer_believes_has_trafficked_some_girls'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_has_trafficked_some_girls',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_india_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_india_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_passport'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_passport',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_manpower'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_manpower',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_broker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_broker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_own_relative_of'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_own_relative_of',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_sex_industry'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_sex_industry',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.victim_believes_is_not_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'victim_believes_is_not_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_companion'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_companion',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.interviewer_believes_is_not_trafficker'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes_is_not_trafficker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterviewPersonBox.who_is_this_contact_of_husband'
        db.add_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_contact_of_husband',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'VictimInterviewPersonBox.who_is_this_relationship'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_relationship')

        # Deleting field 'VictimInterviewPersonBox.who_is_this_role'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'who_is_this_role')

        # Deleting field 'VictimInterviewPersonBox.interviewer_believes'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'interviewer_believes')

        # Deleting field 'VictimInterviewPersonBox.victim_believes'
        db.delete_column(u'dataentry_victiminterviewpersonbox', 'victim_believes')


        # Changing field 'VictimInterviewPersonBox.occupation'
        db.alter_column(u'dataentry_victiminterviewpersonbox', 'occupation', self.gf('django.db.models.fields.CharField')(max_length=50))

    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'activation_key': ('django.db.models.fields.CharField', [], {'default': "'VjBJt0QZDxNVpOlA9epqBZ4zNwgVsNfFFwCokb0T'", 'max_length': '40'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'permission_accounts_manage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_designation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'to': u"orm['accounts.DefaultPermissionsSet']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'accounts.defaultpermissionsset': {
            'Meta': {'object_name': 'DefaultPermissionsSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'permission_accounts_manage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'dataentry.interceptee': {
            'Meta': {'ordering': "['id']", 'object_name': 'Interceptee'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interception_record': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'interceptees'", 'to': u"orm['dataentry.InterceptionRecord']"}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'phone_contact': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'relation_to': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'dataentry.interceptionrecord': {
            'Meta': {'object_name': 'InterceptionRecord'},
            'between_2_12_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'call_subcommittee_chair': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'call_thn_to_cross_check': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caste_not_same_as_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caught_in_lie': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_bus_driver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_church_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_hotel_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_noticed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_other_ngo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_paid': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'contact_paid_how_much': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_police': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_rickshaw_driver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_subcommittee_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_taxi_driver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'couldnt_confirm_job': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_form_received': ('django.db.models.fields.DateTimeField', [], {}),
            'date_time_entered_into_system': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_time_last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_time_of_interception': ('django.db.models.fields.DateTimeField', [], {}),
            'doesnt_know_going_to_india': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doesnt_know_school_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doesnt_know_villiage_details': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'drugged_or_drowsy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fake_medical_documents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'form_entered_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'irfs_entered'", 'to': u"orm['accounts.Account']"}),
            'going_to_gulf_for_work': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_signature': ('django.db.models.fields.BooleanField', [], {}),
            'how_sure_was_trafficking': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interception_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'irf_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'job_too_good_to_be_true': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'less_than_2_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'married_in_past_2_8_weeks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'married_in_past_2_weeks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meeting_someone_across_border': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name_come_up_before': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'name_come_up_before_yes_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'no_address_in_india': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_appointment_letter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_bags_long_trip': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_company_phone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_enrollment_docs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_medical_appointment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_medical_documents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'no_school_phone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'not_enrolled_in_school': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'not_real_job': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_carrying_a_baby': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_carrying_full_bags': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_caste_difference': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_dirty_clothes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_drugged_or_drowsy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_exiting_vehicle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_heading_to_vehicle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_hesitant': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_hurrying': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_in_a_cart': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_in_a_rickshaw': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_in_a_vehicle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_indian_looking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_looked_like_agent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_nervous_or_afraid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_new_clothes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_on_the_phone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_other_sign': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_other_sign_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'noticed_roaming_around': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_typical_village_look': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_village_dress': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_waiting_sitting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_walking_to_border': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'noticed_young_looking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_red_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'other_red_flag_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'over_18_family_doesnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'over_18_family_unwilling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'passport_with_broker': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'refuses_family_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reluctant_family_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reluctant_treatment_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reluctant_villiage_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reported_total_red_flags': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'running_away_over_18': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'running_away_under_18': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'scan_and_submit_same_day': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'scanned_form': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'seen_in_last_month_in_nepal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shopping_overnight_stuff_in_bags': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'staff_noticed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'staff_who_noticed': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'talked_to_aunt_uncle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_brother': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_father': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_grandparent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_mother': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'talked_to_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'talked_to_sister': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trafficker_taken_into_custody': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'traveling_with_someone_not_with_her': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'under_18_cant_contact_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'under_18_family_doesnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'under_18_family_unwilling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'valid_gulf_country_visa': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_going_job': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_going_shopping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_going_study': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_going_treatment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'where_going_visit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'who_in_group_alone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'who_in_group_husbandwife': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'who_in_group_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wife_under_18': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'dataentry.victiminterview': {
            'Meta': {'object_name': 'VictimInterview'},
            'abuse_happened': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'abuse_happened_by_whom': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'abuse_happened_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'amount_victim_would_earn': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'attitude_towards_tiny_hands': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'awareness_before_interception': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'broker_works_in_job_location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'brokers_relation_to_victim': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'case_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'companion_with_when_intercepted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'date_time_entered_into_system': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_time_last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'family_pressured_victim': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'family_will_try_sending_again': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'guardian_knew_was_travelling_to_india': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'has_signature': ('django.db.models.fields.BooleanField', [], {}),
            'how_can_we_serve_you_better': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'how_many_others_in_situation': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'interviewer_recommendation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'legal_action_against_traffickers': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'legal_action_dofe_against_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'legal_action_fir_against_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'manpower_involved': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'migration_plans': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'migration_plans_second': ('django.db.models.fields.BooleanField', [], {'max_length': '255'}),
            'money_changed_hands_broker_companion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number_broker_made_similar_promises_to': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_husband_trafficker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_person_in_india': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_place_involved_in_trafficking': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_someone_involved_in_trafficking': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_someone_met_along_the_way': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_people_and_places_involved': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'others_in_situation_age_of_youngest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'passport_made': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'permission_to_use_photograph': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'planning_to_meet_companion_later': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'primary_motivation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reason_no_legal': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reason_no_legal_interference_by_powerful_people_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reason_no_legal_interference_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reason_no_legal_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'reported_total_situational_alarms': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'scanned_form': ('django.db.models.fields.files.FileField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'statement_read_before_beginning': ('django.db.models.fields.BooleanField', [], {}),
            'tiny_hands_rating_border_staff': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tiny_hands_rating_shelter_accommodations': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tiny_hands_rating_shelter_staff': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'tiny_hands_rating_trafficking_awareness': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'victim_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_age': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_beliefs_now': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_caste': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_education_level': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_family_economic_situation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_feels_safe_at_home': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_first_time_crossing_border': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_gender': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'victim_guardian_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_drinks_alcohol': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_uses_drugs': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_had_suicidal_thoughts': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_has_worked_in_sex_industry': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_heard_gospel': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'victim_height': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_home_had_emotional_abuse': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_home_had_physical_abuse': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_home_had_sexual_abuse': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_how_expense_was_paid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_how_expense_was_paid_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'victim_how_long_known_broker_months': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_known_broker_years': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_stayed_between_days': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_stayed_between_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_met_broker': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_how_met_broker_mobile_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_is_literate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_knew_details_about_destination': ('django.db.models.fields.BooleanField', [], {}),
            'victim_lives_with': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_marital_status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_married_to_broker_months': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_married_to_broker_years': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'victim_num_in_family': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_occupation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_parents_marital_status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_passport_with_broker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_place_worked_involved_sending_girls_overseas': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_primary_guardian': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_primary_means_of_travel': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'victim_recruited_in_village': ('django.db.models.fields.BooleanField', [], {}),
            'victim_stayed_somewhere_between': ('django.db.models.fields.BooleanField', [], {}),
            'victim_traveled_with_broker_companion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_wants_to_go_home': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_was_free_to_go_out': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_was_free_to_go_out_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_was_hidden': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_was_hidden_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_weight': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vif_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'who_meeting_at_border': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'dataentry.victiminterviewlocationbox': {
            'Meta': {'object_name': 'VictimInterviewLocationBox'},
            'associated_with_person': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'associated_with_person_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'compound_wall': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gate_color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewer_believes_not_used_for_trafficking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'interviewer_believes_suspect_used_for_trafficking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'interviewer_believes_trafficked_many_girls': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'interviewer_believes_trafficked_some_girls': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location_in_town': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nearby_landmarks': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nearby_signboards': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'number_of_levels': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'person_in_charge': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'roof_color': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'roof_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'signboard': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_believes_not_used_for_trafficking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_believes_suspect_used_for_trafficking': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_believes_trafficked_many_girls': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_believes_trafficked_some_girls': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_interview': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'location_boxes'", 'to': u"orm['dataentry.VictimInterview']"}),
            'what_kind_place_brothel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_bus_station': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_factory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_hotel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_persons_house': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_shop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'what_kind_place_train_station': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_destination': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_india_meetpoint': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_known_location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_manpower': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_nepal_meet_point': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_passport': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_sex_industry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'which_place_transit_hideout': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'dataentry.victiminterviewpersonbox': {
            'Meta': {'object_name': 'VictimInterviewPersonBox'},
            'address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'age': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'appearance_other': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'associated_with_place': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'associated_with_place_value': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'height': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewer_believes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'occupation': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'occupation_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'physical_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'political_party': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'political_party_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_believes': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_interview': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'person_boxes'", 'to': u"orm['dataentry.VictimInterview']"}),
            'weight': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'where_spends_time': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'who_is_this_relationship': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'who_is_this_role': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['dataentry']