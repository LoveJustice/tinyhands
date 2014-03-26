# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'InterceptionRecord.irf_number'
        db.add_column(u'dataentry_interceptionrecord', 'irf_number',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'InterceptionRecord.time'
        db.add_column(u'dataentry_interceptionrecord', 'time',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'InterceptionRecord.number_of_victims'
        db.add_column(u'dataentry_interceptionrecord', 'number_of_victims',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'InterceptionRecord.number_of_traffickers'
        db.add_column(u'dataentry_interceptionrecord', 'number_of_traffickers',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'InterceptionRecord.location'
        db.add_column(u'dataentry_interceptionrecord', 'location',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'InterceptionRecord.staff_name'
        db.add_column(u'dataentry_interceptionrecord', 'staff_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


        # Changing field 'InterceptionRecord.who_in_group'
        db.alter_column(u'dataentry_interceptionrecord', 'who_in_group', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):
        # Deleting field 'InterceptionRecord.irf_number'
        db.delete_column(u'dataentry_interceptionrecord', 'irf_number')

        # Deleting field 'InterceptionRecord.time'
        db.delete_column(u'dataentry_interceptionrecord', 'time')

        # Deleting field 'InterceptionRecord.number_of_victims'
        db.delete_column(u'dataentry_interceptionrecord', 'number_of_victims')

        # Deleting field 'InterceptionRecord.number_of_traffickers'
        db.delete_column(u'dataentry_interceptionrecord', 'number_of_traffickers')

        # Deleting field 'InterceptionRecord.location'
        db.delete_column(u'dataentry_interceptionrecord', 'location')

        # Deleting field 'InterceptionRecord.staff_name'
        db.delete_column(u'dataentry_interceptionrecord', 'staff_name')


        # User chose to not deal with backwards NULL issues for 'InterceptionRecord.who_in_group'
        raise RuntimeError("Cannot reverse this migration. 'InterceptionRecord.who_in_group' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'InterceptionRecord.who_in_group'
        db.alter_column(u'dataentry_interceptionrecord', 'who_in_group', self.gf('django.db.models.fields.IntegerField')())

    models = {
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
        u'dataentry.account': {
            'Meta': {'object_name': 'Account'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'dataentry.interceptionrecord': {
            'Meta': {'object_name': 'InterceptionRecord'},
            'between_2_12_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {}),
            'caste_not_same_as_relative': ('django.db.models.fields.BooleanField', [], {}),
            'caught_in_lie': ('django.db.models.fields.BooleanField', [], {}),
            'drugged_or_drowsy': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irf_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'less_than_2_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'married_in_past_2_8_weeks': ('django.db.models.fields.BooleanField', [], {}),
            'married_in_past_2_weeks': ('django.db.models.fields.BooleanField', [], {}),
            'meeting_someone_across_border': ('django.db.models.fields.BooleanField', [], {}),
            'number_of_traffickers': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_victims': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'seen_in_last_month_in_nepal': ('django.db.models.fields.BooleanField', [], {}),
            'staff_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'time': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'traveling_with_someone_not_with_her': ('django.db.models.fields.BooleanField', [], {}),
            'who_in_group': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wife_under_18': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['dataentry']