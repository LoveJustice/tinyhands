# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VictimInterview.manpower_involved'
        db.add_column(u'dataentry_victiminterview', 'manpower_involved',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_recruited_in_village'
        db.add_column(u'dataentry_victiminterview', 'victim_recruited_in_village',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_dad'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_dad',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_mom'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_mom',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_uncle'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_uncle',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_aunt'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_aunt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_bro'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_bro',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_sister'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_sister',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_own_other_relative'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_other_relative',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_friend'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_friend',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_agent'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_agent',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_husband'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_husband',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_boyfriend'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_boyfriend',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_neighbor'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_neighbor',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_recently_met'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_recently_met',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_contractor'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_contractor',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_other'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_married_to_broker_years'
        db.add_column(u'dataentry_victiminterview', 'victim_married_to_broker_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_married_to_broker_months'
        db.add_column(u'dataentry_victiminterview', 'victim_married_to_broker_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_from_community'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_from_community',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_at_work'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_work',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_at_school'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_school',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_job_advertisement'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_job_advertisement',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_he_approached_me'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_he_approached_me',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_through_friends'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_through_friends',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_through_family'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_through_family',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_at_wedding'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_wedding',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_in_a_vehicle'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_in_a_vehicle',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_in_a_hospital'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_in_a_hospital',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_went_myself'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_went_myself',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_called_my_mobile'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_called_my_mobile',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_other'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_met_broker_mobile_explanation'
        db.add_column(u'dataentry_victiminterview', 'victim_how_met_broker_mobile_explanation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_long_known_broker_years'
        db.add_column(u'dataentry_victiminterview', 'victim_how_long_known_broker_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_long_known_broker_months'
        db.add_column(u'dataentry_victiminterview', 'victim_how_long_known_broker_months',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_expense_was_paid_paid_myself'
        db.add_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_paid_myself',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_expense_was_paid_broker_paid_all'
        db.add_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_broker_paid_all',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_expense_was_paid_gave_money_to_broker'
        db.add_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_gave_money_to_broker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_expense_was_paid_broker_gave_loan'
        db.add_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_broker_gave_loan',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_expense_was_paid_amount'
        db.add_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_amount',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.broker_works_in_job_location_no'
        db.add_column(u'dataentry_victiminterview', 'broker_works_in_job_location_no',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.broker_works_in_job_location_yes'
        db.add_column(u'dataentry_victiminterview', 'broker_works_in_job_location_yes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.broker_works_in_job_location_dont_know'
        db.add_column(u'dataentry_victiminterview', 'broker_works_in_job_location_dont_know',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.amount_victim_would_earn'
        db.add_column(u'dataentry_victiminterview', 'amount_victim_would_earn',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.number_broker_made_similar_promises_to'
        db.add_column(u'dataentry_victiminterview', 'number_broker_made_similar_promises_to',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_first_time_crossing_border'
        db.add_column(u'dataentry_victiminterview', 'victim_first_time_crossing_border',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_tourist_bus'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_tourist_bus',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_motorbike'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_motorbike',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_private_car'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_private_car',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_local_bus'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_local_bus',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_microbus'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_microbus',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_plane'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_plane',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_other'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_means_of_travel_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_stayed_somewhere_between'
        db.add_column(u'dataentry_victiminterview', 'victim_stayed_somewhere_between',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_long_stayed_between_days'
        db.add_column(u'dataentry_victiminterview', 'victim_how_long_stayed_between_days',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_how_long_stayed_between_start_date'
        db.add_column(u'dataentry_victiminterview', 'victim_how_long_stayed_between_start_date',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_was_hidden'
        db.add_column(u'dataentry_victiminterview', 'victim_was_hidden',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_was_hidden_explanation'
        db.add_column(u'dataentry_victiminterview', 'victim_was_hidden_explanation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_was_free_to_go_out'
        db.add_column(u'dataentry_victiminterview', 'victim_was_free_to_go_out',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_was_free_to_go_out_explanation'
        db.add_column(u'dataentry_victiminterview', 'victim_was_free_to_go_out_explanation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.how_many_others_in_situation'
        db.add_column(u'dataentry_victiminterview', 'how_many_others_in_situation',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.others_in_situation_age_of_youngest'
        db.add_column(u'dataentry_victiminterview', 'others_in_situation_age_of_youngest',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_no_passport_made'
        db.add_column(u'dataentry_victiminterview', 'passport_made_no_passport_made',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_real_passport_made'
        db.add_column(u'dataentry_victiminterview', 'passport_made_real_passport_made',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_passport_included_false_name'
        db.add_column(u'dataentry_victiminterview', 'passport_made_passport_included_false_name',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_passport_included_other_false_info'
        db.add_column(u'dataentry_victiminterview', 'passport_made_passport_included_other_false_info',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.passport_made_passport_was_fake'
        db.add_column(u'dataentry_victiminterview', 'passport_made_passport_was_fake',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_passport_with_broker'
        db.add_column(u'dataentry_victiminterview', 'victim_passport_with_broker',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_sexual_harassment'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_sexual_harassment',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_sexual_abuse'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_sexual_abuse',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_physical_abuse'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_physical_abuse',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_threats'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_threats',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_denied_proper_food'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_denied_proper_food',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_forced_to_take_drugs'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_forced_to_take_drugs',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_by_whom'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_by_whom',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.abuse_happened_explanation'
        db.add_column(u'dataentry_victiminterview', 'abuse_happened_explanation',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_traveled_with_broker_companion_yes'
        db.add_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_yes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_traveled_with_broker_companion_no'
        db.add_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_no',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_traveled_with_broker_companion_broker_took_me_to_border'
        db.add_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_broker_took_me_to_border',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.companion_with_when_intercepted'
        db.add_column(u'dataentry_victiminterview', 'companion_with_when_intercepted',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.planning_to_meet_companion_later'
        db.add_column(u'dataentry_victiminterview', 'planning_to_meet_companion_later',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.money_changed_hands_broker_companion_no'
        db.add_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_no',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.money_changed_hands_broker_companion_dont_know'
        db.add_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_dont_know',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.money_changed_hands_broker_companion_broker_gave_money'
        db.add_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_broker_gave_money',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.money_changed_hands_broker_companion_companion_gave_money'
        db.add_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_companion_gave_money',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.meeting_at_border_yes'
        db.add_column(u'dataentry_victiminterview', 'meeting_at_border_yes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.meeting_at_border_no'
        db.add_column(u'dataentry_victiminterview', 'meeting_at_border_no',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.meeting_at_border_meeting_broker'
        db.add_column(u'dataentry_victiminterview', 'meeting_at_border_meeting_broker',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.meeting_at_border_meeting_companion'
        db.add_column(u'dataentry_victiminterview', 'meeting_at_border_meeting_companion',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_knew_details_about_destination'
        db.add_column(u'dataentry_victiminterview', 'victim_knew_details_about_destination',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.other_involved_person_in_india'
        db.add_column(u'dataentry_victiminterview', 'other_involved_person_in_india',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.other_involved_husband_trafficker'
        db.add_column(u'dataentry_victiminterview', 'other_involved_husband_trafficker',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.other_involved_someone_met_along_the_way'
        db.add_column(u'dataentry_victiminterview', 'other_involved_someone_met_along_the_way',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.other_involved_someone_involved_in_trafficking'
        db.add_column(u'dataentry_victiminterview', 'other_involved_someone_involved_in_trafficking',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.other_involved_place_involved_in_trafficking'
        db.add_column(u'dataentry_victiminterview', 'other_involved_place_involved_in_trafficking',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_has_worked_in_sex_industry'
        db.add_column(u'dataentry_victiminterview', 'victim_has_worked_in_sex_industry',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_place_worked_involved_sending_girls_overseas'
        db.add_column(u'dataentry_victiminterview', 'victim_place_worked_involved_sending_girls_overseas',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'VictimInterview.manpower_involved'
        db.delete_column(u'dataentry_victiminterview', 'manpower_involved')

        # Deleting field 'VictimInterview.victim_recruited_in_village'
        db.delete_column(u'dataentry_victiminterview', 'victim_recruited_in_village')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_dad'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_dad')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_mom'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_mom')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_uncle'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_uncle')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_aunt'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_aunt')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_bro'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_bro')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_sister'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_sister')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_own_other_relative'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_own_other_relative')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_friend'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_friend')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_agent'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_agent')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_husband'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_husband')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_boyfriend'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_boyfriend')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_neighbor'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_neighbor')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_recently_met'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_recently_met')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_contractor'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_contractor')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_other'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value')

        # Deleting field 'VictimInterview.victim_married_to_broker_years'
        db.delete_column(u'dataentry_victiminterview', 'victim_married_to_broker_years')

        # Deleting field 'VictimInterview.victim_married_to_broker_months'
        db.delete_column(u'dataentry_victiminterview', 'victim_married_to_broker_months')

        # Deleting field 'VictimInterview.victim_how_met_broker_from_community'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_from_community')

        # Deleting field 'VictimInterview.victim_how_met_broker_at_work'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_work')

        # Deleting field 'VictimInterview.victim_how_met_broker_at_school'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_school')

        # Deleting field 'VictimInterview.victim_how_met_broker_job_advertisement'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_job_advertisement')

        # Deleting field 'VictimInterview.victim_how_met_broker_he_approached_me'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_he_approached_me')

        # Deleting field 'VictimInterview.victim_how_met_broker_through_friends'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_through_friends')

        # Deleting field 'VictimInterview.victim_how_met_broker_through_family'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_through_family')

        # Deleting field 'VictimInterview.victim_how_met_broker_at_wedding'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_at_wedding')

        # Deleting field 'VictimInterview.victim_how_met_broker_in_a_vehicle'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_in_a_vehicle')

        # Deleting field 'VictimInterview.victim_how_met_broker_in_a_hospital'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_in_a_hospital')

        # Deleting field 'VictimInterview.victim_how_met_broker_went_myself'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_went_myself')

        # Deleting field 'VictimInterview.victim_how_met_broker_called_my_mobile'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_called_my_mobile')

        # Deleting field 'VictimInterview.victim_how_met_broker_other'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_other')

        # Deleting field 'VictimInterview.victim_how_met_broker_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_other_value')

        # Deleting field 'VictimInterview.victim_how_met_broker_mobile_explanation'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_met_broker_mobile_explanation')

        # Deleting field 'VictimInterview.victim_how_long_known_broker_years'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_long_known_broker_years')

        # Deleting field 'VictimInterview.victim_how_long_known_broker_months'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_long_known_broker_months')

        # Deleting field 'VictimInterview.victim_how_expense_was_paid_paid_myself'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_paid_myself')

        # Deleting field 'VictimInterview.victim_how_expense_was_paid_broker_paid_all'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_broker_paid_all')

        # Deleting field 'VictimInterview.victim_how_expense_was_paid_gave_money_to_broker'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_gave_money_to_broker')

        # Deleting field 'VictimInterview.victim_how_expense_was_paid_broker_gave_loan'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_broker_gave_loan')

        # Deleting field 'VictimInterview.victim_how_expense_was_paid_amount'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_expense_was_paid_amount')

        # Deleting field 'VictimInterview.broker_works_in_job_location_no'
        db.delete_column(u'dataentry_victiminterview', 'broker_works_in_job_location_no')

        # Deleting field 'VictimInterview.broker_works_in_job_location_yes'
        db.delete_column(u'dataentry_victiminterview', 'broker_works_in_job_location_yes')

        # Deleting field 'VictimInterview.broker_works_in_job_location_dont_know'
        db.delete_column(u'dataentry_victiminterview', 'broker_works_in_job_location_dont_know')

        # Deleting field 'VictimInterview.amount_victim_would_earn'
        db.delete_column(u'dataentry_victiminterview', 'amount_victim_would_earn')

        # Deleting field 'VictimInterview.number_broker_made_similar_promises_to'
        db.delete_column(u'dataentry_victiminterview', 'number_broker_made_similar_promises_to')

        # Deleting field 'VictimInterview.victim_first_time_crossing_border'
        db.delete_column(u'dataentry_victiminterview', 'victim_first_time_crossing_border')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_tourist_bus'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_tourist_bus')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_motorbike'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_motorbike')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_private_car'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_private_car')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_local_bus'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_local_bus')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_microbus'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_microbus')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_plane'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_plane')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_other'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other')

        # Deleting field 'VictimInterview.victim_primary_means_of_travel_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_means_of_travel_other_value')

        # Deleting field 'VictimInterview.victim_stayed_somewhere_between'
        db.delete_column(u'dataentry_victiminterview', 'victim_stayed_somewhere_between')

        # Deleting field 'VictimInterview.victim_how_long_stayed_between_days'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_long_stayed_between_days')

        # Deleting field 'VictimInterview.victim_how_long_stayed_between_start_date'
        db.delete_column(u'dataentry_victiminterview', 'victim_how_long_stayed_between_start_date')

        # Deleting field 'VictimInterview.victim_was_hidden'
        db.delete_column(u'dataentry_victiminterview', 'victim_was_hidden')

        # Deleting field 'VictimInterview.victim_was_hidden_explanation'
        db.delete_column(u'dataentry_victiminterview', 'victim_was_hidden_explanation')

        # Deleting field 'VictimInterview.victim_was_free_to_go_out'
        db.delete_column(u'dataentry_victiminterview', 'victim_was_free_to_go_out')

        # Deleting field 'VictimInterview.victim_was_free_to_go_out_explanation'
        db.delete_column(u'dataentry_victiminterview', 'victim_was_free_to_go_out_explanation')

        # Deleting field 'VictimInterview.how_many_others_in_situation'
        db.delete_column(u'dataentry_victiminterview', 'how_many_others_in_situation')

        # Deleting field 'VictimInterview.others_in_situation_age_of_youngest'
        db.delete_column(u'dataentry_victiminterview', 'others_in_situation_age_of_youngest')

        # Deleting field 'VictimInterview.passport_made_no_passport_made'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_no_passport_made')

        # Deleting field 'VictimInterview.passport_made_real_passport_made'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_real_passport_made')

        # Deleting field 'VictimInterview.passport_made_passport_included_false_name'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_passport_included_false_name')

        # Deleting field 'VictimInterview.passport_made_passport_included_other_false_info'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_passport_included_other_false_info')

        # Deleting field 'VictimInterview.passport_made_passport_was_fake'
        db.delete_column(u'dataentry_victiminterview', 'passport_made_passport_was_fake')

        # Deleting field 'VictimInterview.victim_passport_with_broker'
        db.delete_column(u'dataentry_victiminterview', 'victim_passport_with_broker')

        # Deleting field 'VictimInterview.abuse_happened_sexual_harassment'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_sexual_harassment')

        # Deleting field 'VictimInterview.abuse_happened_sexual_abuse'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_sexual_abuse')

        # Deleting field 'VictimInterview.abuse_happened_physical_abuse'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_physical_abuse')

        # Deleting field 'VictimInterview.abuse_happened_threats'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_threats')

        # Deleting field 'VictimInterview.abuse_happened_denied_proper_food'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_denied_proper_food')

        # Deleting field 'VictimInterview.abuse_happened_forced_to_take_drugs'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_forced_to_take_drugs')

        # Deleting field 'VictimInterview.abuse_happened_by_whom'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_by_whom')

        # Deleting field 'VictimInterview.abuse_happened_explanation'
        db.delete_column(u'dataentry_victiminterview', 'abuse_happened_explanation')

        # Deleting field 'VictimInterview.victim_traveled_with_broker_companion_yes'
        db.delete_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_yes')

        # Deleting field 'VictimInterview.victim_traveled_with_broker_companion_no'
        db.delete_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_no')

        # Deleting field 'VictimInterview.victim_traveled_with_broker_companion_broker_took_me_to_border'
        db.delete_column(u'dataentry_victiminterview', 'victim_traveled_with_broker_companion_broker_took_me_to_border')

        # Deleting field 'VictimInterview.companion_with_when_intercepted'
        db.delete_column(u'dataentry_victiminterview', 'companion_with_when_intercepted')

        # Deleting field 'VictimInterview.planning_to_meet_companion_later'
        db.delete_column(u'dataentry_victiminterview', 'planning_to_meet_companion_later')

        # Deleting field 'VictimInterview.money_changed_hands_broker_companion_no'
        db.delete_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_no')

        # Deleting field 'VictimInterview.money_changed_hands_broker_companion_dont_know'
        db.delete_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_dont_know')

        # Deleting field 'VictimInterview.money_changed_hands_broker_companion_broker_gave_money'
        db.delete_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_broker_gave_money')

        # Deleting field 'VictimInterview.money_changed_hands_broker_companion_companion_gave_money'
        db.delete_column(u'dataentry_victiminterview', 'money_changed_hands_broker_companion_companion_gave_money')

        # Deleting field 'VictimInterview.meeting_at_border_yes'
        db.delete_column(u'dataentry_victiminterview', 'meeting_at_border_yes')

        # Deleting field 'VictimInterview.meeting_at_border_no'
        db.delete_column(u'dataentry_victiminterview', 'meeting_at_border_no')

        # Deleting field 'VictimInterview.meeting_at_border_meeting_broker'
        db.delete_column(u'dataentry_victiminterview', 'meeting_at_border_meeting_broker')

        # Deleting field 'VictimInterview.meeting_at_border_meeting_companion'
        db.delete_column(u'dataentry_victiminterview', 'meeting_at_border_meeting_companion')

        # Deleting field 'VictimInterview.victim_knew_details_about_destination'
        db.delete_column(u'dataentry_victiminterview', 'victim_knew_details_about_destination')

        # Deleting field 'VictimInterview.other_involved_person_in_india'
        db.delete_column(u'dataentry_victiminterview', 'other_involved_person_in_india')

        # Deleting field 'VictimInterview.other_involved_husband_trafficker'
        db.delete_column(u'dataentry_victiminterview', 'other_involved_husband_trafficker')

        # Deleting field 'VictimInterview.other_involved_someone_met_along_the_way'
        db.delete_column(u'dataentry_victiminterview', 'other_involved_someone_met_along_the_way')

        # Deleting field 'VictimInterview.other_involved_someone_involved_in_trafficking'
        db.delete_column(u'dataentry_victiminterview', 'other_involved_someone_involved_in_trafficking')

        # Deleting field 'VictimInterview.other_involved_place_involved_in_trafficking'
        db.delete_column(u'dataentry_victiminterview', 'other_involved_place_involved_in_trafficking')

        # Deleting field 'VictimInterview.victim_has_worked_in_sex_industry'
        db.delete_column(u'dataentry_victiminterview', 'victim_has_worked_in_sex_industry')

        # Deleting field 'VictimInterview.victim_place_worked_involved_sending_girls_overseas'
        db.delete_column(u'dataentry_victiminterview', 'victim_place_worked_involved_sending_girls_overseas')


    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
            'activation_key': ('django.db.models.fields.CharField', [], {'default': "'8LTYl9tsyqlbSuYbESADnNCJspxOC8r2bmWqeAg7'", 'max_length': '40'}),
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
            'abuse_happened_by_whom': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'abuse_happened_denied_proper_food': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_happened_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'abuse_happened_forced_to_take_drugs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_happened_physical_abuse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_happened_sexual_abuse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_happened_sexual_harassment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'abuse_happened_threats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'amount_victim_would_earn': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'broker_works_in_job_location_dont_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'broker_works_in_job_location_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'broker_works_in_job_location_yes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_agent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_boyfriend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_contractor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_friend': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_husband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_neighbor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'brokers_relation_to_victim_own_aunt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_bro': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_dad': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_mom': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_other_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_sister': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_own_uncle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'brokers_relation_to_victim_recently_met': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'companion_with_when_intercepted': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'date_time_entered_into_system': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_time_last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'how_many_others_in_situation': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'manpower_involved': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'meeting_at_border_meeting_broker': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meeting_at_border_meeting_companion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meeting_at_border_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meeting_at_border_yes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_arranged_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_education': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_eloping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_baby_care': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_broker_didnt_say': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_brothel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_factory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_hotel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_household': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_laborer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'migration_plans_job_shop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_medical_treatment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_meet_own_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'migration_plans_shopping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_travel_tour': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_visit_brokers_home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'money_changed_hands_broker_companion_broker_gave_money': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'money_changed_hands_broker_companion_companion_gave_money': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'money_changed_hands_broker_companion_dont_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'money_changed_hands_broker_companion_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number_broker_made_similar_promises_to': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_husband_trafficker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_person_in_india': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_place_involved_in_trafficking': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_someone_involved_in_trafficking': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'other_involved_someone_met_along_the_way': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'others_in_situation_age_of_youngest': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'passport_made_no_passport_made': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'passport_made_passport_included_false_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'passport_made_passport_included_other_false_info': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'passport_made_passport_was_fake': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'passport_made_real_passport_made': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_to_use_photograph': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'planning_to_meet_companion_later': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'primary_motivation_bad_home_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_didnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_family_debt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_get_education': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_love_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'primary_motivation_personal_debt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_support_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_support_myself': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_tour_travel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'statement_read_before_beginning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_age': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_caste_brahmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_chhetri': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_dalit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_jaisi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_madeshi_terai': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_magar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_mongolian': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_muslim': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_newar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_caste_tamang': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_caste_thakuri': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_11_12': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_bachelors': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_grade_4_8': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_grade_9_10': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_informal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_masters': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_none': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_education_level_slc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_first_time_crossing_border': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_gender': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'victim_guardian_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_has_worked_in_sex_industry': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_height': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_how_expense_was_paid_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'victim_how_expense_was_paid_broker_gave_loan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_expense_was_paid_broker_paid_all': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_expense_was_paid_gave_money_to_broker': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_expense_was_paid_paid_myself': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_long_known_broker_months': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_known_broker_years': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_stayed_between_days': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_long_stayed_between_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'victim_how_met_broker_at_school': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_at_wedding': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_at_work': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_called_my_mobile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_from_community': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_he_approached_me': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_in_a_hospital': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_in_a_vehicle': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_job_advertisement': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_mobile_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_how_met_broker_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_how_met_broker_through_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_through_friends': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_how_met_broker_went_myself': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_is_literate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_knew_details_about_destination': ('django.db.models.fields.BooleanField', [], {}),
            'victim_lives_with_alone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_friends': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_husband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_husbands_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_lives_with_own_parents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_abandoned_by_husband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_divorced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_husband_has_other_wives': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_married': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_single': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status_widow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_married_to_broker_months': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_married_to_broker_years': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'victim_num_in_family': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_occupation_animal_husbandry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_business_owner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_domestic_work': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_factory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_farmer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_hotel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_housewife': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_migrant_worker': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_occupation_shopkeeper': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_tailoring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_unemployed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_occupation_wage_laborer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_divorced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_separated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_status_father_has_other_wives': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_status_married': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_status_single': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_parents_marital_status_widow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_passport_with_broker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_place_worked_involved_sending_girls_overseas': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_primary_guardian_husband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_guardian_no_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_guardian_non_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_guardian_other_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_guardian_own_parents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_local_bus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_microbus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_motorbike': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_primary_means_of_travel_plane': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_private_car': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_primary_means_of_travel_tourist_bus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_recruited_in_village': ('django.db.models.fields.BooleanField', [], {}),
            'victim_stayed_somewhere_between': ('django.db.models.fields.BooleanField', [], {}),
            'victim_traveled_with_broker_companion_broker_took_me_to_border': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_traveled_with_broker_companion_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_traveled_with_broker_companion_yes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_was_free_to_go_out': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_was_free_to_go_out_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_was_hidden': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_was_hidden_explanation': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'victim_weight': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_bihar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_delhi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_dubai': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_gulf': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_gulf_didnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_gulf_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_gulf_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_india': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_india_didnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_india_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_india_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_jaipur': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_kolkata': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_kuwait': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_lebanon': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_malaysia': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_mumbai': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_oman': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_pune': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_qatar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_rajastan': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_saudi_arabia': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_where_going_surat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vif_number': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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