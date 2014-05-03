# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VictimInterview.victim_where_going_gulf_other'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_gulf_other')

        # Deleting field 'VictimInterview.victim_where_going_india'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_india')

        # Deleting field 'VictimInterview.victim_primary_motivation'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_motivation')

        # Deleting field 'VictimInterview.victim_primary_motivation_other_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_primary_motivation_other_value')

        # Deleting field 'VictimInterview.victim_guardian_address_phone'
        db.delete_column(u'dataentry_victiminterview', 'victim_guardian_address_phone')

        # Adding field 'VictimInterview.victim_guardian_phone'
        db.add_column(u'dataentry_victiminterview', 'victim_guardian_phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_support_myself'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_support_myself',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_support_family'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_support_family',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_personal_debt'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_personal_debt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_family_debt'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_family_debt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_love_marriage'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_love_marriage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_bad_home_marriage'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_bad_home_marriage',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_get_an_education'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_get_an_education',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_tour_travel'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_tour_travel',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_didnt_know'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_didnt_know',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_other'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_other',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.primary_motivation_other_value'
        db.add_column(u'dataentry_victiminterview', 'primary_motivation_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_region'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_region',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_other_gulf_value'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_other_gulf_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_other_india_value'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_other_india_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.manpower_involved'
        db.add_column(u'dataentry_victiminterview', 'manpower_involved',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_recruited_in_village'
        db.add_column(u'dataentry_victiminterview', 'victim_recruited_in_village',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.add_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_married_to_broker_years'
        db.add_column(u'dataentry_victiminterview', 'victim_married_to_broker_years',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'VictimInterview.victim_where_going_gulf_other'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_gulf_other',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_where_going_india'
        db.add_column(u'dataentry_victiminterview', 'victim_where_going_india',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_motivation'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_motivation',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_primary_motivation_other_value'
        db.add_column(u'dataentry_victiminterview', 'victim_primary_motivation_other_value',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VictimInterview.victim_guardian_address_phone'
        db.add_column(u'dataentry_victiminterview', 'victim_guardian_address_phone',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'VictimInterview.victim_guardian_phone'
        db.delete_column(u'dataentry_victiminterview', 'victim_guardian_phone')

        # Deleting field 'VictimInterview.primary_motivation_support_myself'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_support_myself')

        # Deleting field 'VictimInterview.primary_motivation_support_family'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_support_family')

        # Deleting field 'VictimInterview.primary_motivation_personal_debt'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_personal_debt')

        # Deleting field 'VictimInterview.primary_motivation_family_debt'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_family_debt')

        # Deleting field 'VictimInterview.primary_motivation_love_marriage'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_love_marriage')

        # Deleting field 'VictimInterview.primary_motivation_bad_home_marriage'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_bad_home_marriage')

        # Deleting field 'VictimInterview.primary_motivation_get_an_education'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_get_an_education')

        # Deleting field 'VictimInterview.primary_motivation_tour_travel'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_tour_travel')

        # Deleting field 'VictimInterview.primary_motivation_didnt_know'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_didnt_know')

        # Deleting field 'VictimInterview.primary_motivation_other'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_other')

        # Deleting field 'VictimInterview.primary_motivation_other_value'
        db.delete_column(u'dataentry_victiminterview', 'primary_motivation_other_value')

        # Deleting field 'VictimInterview.victim_where_going_region'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_region')

        # Deleting field 'VictimInterview.victim_where_going_other_gulf_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_other_gulf_value')

        # Deleting field 'VictimInterview.victim_where_going_other_india_value'
        db.delete_column(u'dataentry_victiminterview', 'victim_where_going_other_india_value')

        # Deleting field 'VictimInterview.manpower_involved'
        db.delete_column(u'dataentry_victiminterview', 'manpower_involved')

        # Deleting field 'VictimInterview.victim_recruited_in_village'
        db.delete_column(u'dataentry_victiminterview', 'victim_recruited_in_village')

        # Deleting field 'VictimInterview.brokers_relation_to_victim'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim')

        # Deleting field 'VictimInterview.brokers_relation_to_victim_other_value'
        db.delete_column(u'dataentry_victiminterview', 'brokers_relation_to_victim_other_value')

        # Deleting field 'VictimInterview.victim_married_to_broker_years'
        db.delete_column(u'dataentry_victiminterview', 'victim_married_to_broker_years')


    models = {
        u'accounts.account': {
            'Meta': {'object_name': 'Account'},
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
            'Meta': {'object_name': 'Interceptee'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
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
            'contact_paid_how_much': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_paid_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_paid_yes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_police': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_rickshaw_driver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_subcommittee_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_taxi_driver': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'couldnt_confirm_job': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_form_received': ('django.db.models.fields.DateTimeField', [], {}),
            'date_time_of_interception': ('django.db.models.fields.DateTimeField', [], {}),
            'doesnt_know_going_to_india': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doesnt_know_school_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doesnt_know_villiage_details': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'drugged_or_drowsy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fake_medical_documents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'form_entered_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'irfs_entered'", 'to': u"orm['accounts.Account']"}),
            'going_to_gulf_for_work': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_signature': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'how_sure_was_trafficking': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interception_type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'irf_number': ('django.db.models.fields.IntegerField', [], {}),
            'job_too_good_to_be_true': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'less_than_2_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'married_in_past_2_8_weeks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'married_in_past_2_weeks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'meeting_someone_across_border': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name_come_up_before_no': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name_come_up_before_yes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {}),
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
            'brokers_relation_to_victim': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'brokers_relation_to_victim_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interviewer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'manpower_involved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_arranged_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_education': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_eloping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_baby_care': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_broker_did_not_say': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_brothel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_factory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_hotel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_household': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_laborer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_shop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_job_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'migration_plans_medical_treatment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_meet_own_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'migration_plans_shopping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_travel_tour': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'migration_plans_visit_brokers_home': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'primary_motivation_bad_home_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_didnt_know': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_family_debt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_get_an_education': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_love_marriage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'primary_motivation_personal_debt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_support_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_support_myself': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_motivation_tour_travel': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_age': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_caste': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'victim_caste_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_education_level': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_gender': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'victim_guardian_address_district': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_vdc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_address_ward': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_guardian_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_height': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_is_literate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'victim_lives_with_alone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_friends': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_husband': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_husbands_family': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other_relative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_lives_with_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_lives_with_own_parents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_marital_status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_married_to_broker_years': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_num_in_family': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'victim_occupation': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_occupation_other_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_parents_marital_status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_primary_guardian': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'victim_recruited_in_village': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'victim_weight': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_other_gulf_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_other_india_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'victim_where_going_region': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'vif_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dataentry']