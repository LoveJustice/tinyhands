# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Account'
        db.create_table(u'dataentry_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'dataentry', ['Account'])

        # Adding M2M table for field groups on 'Account'
        m2m_table_name = db.shorten_name(u'dataentry_account_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm[u'dataentry.account'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['account_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Account'
        m2m_table_name = db.shorten_name(u'dataentry_account_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm[u'dataentry.account'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['account_id', 'permission_id'])

        # Adding model 'InterceptionRecord'
        db.create_table(u'dataentry_interceptionrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('who_in_group', self.gf('django.db.models.fields.IntegerField')()),
            ('drugged_or_drowsy', self.gf('django.db.models.fields.BooleanField')()),
            ('meeting_someone_across_border', self.gf('django.db.models.fields.BooleanField')()),
            ('seen_in_last_month_in_nepal', self.gf('django.db.models.fields.BooleanField')()),
            ('traveling_with_someone_not_with_her', self.gf('django.db.models.fields.BooleanField')()),
            ('wife_under_18', self.gf('django.db.models.fields.BooleanField')()),
            ('married_in_past_2_weeks', self.gf('django.db.models.fields.BooleanField')()),
            ('married_in_past_2_8_weeks', self.gf('django.db.models.fields.BooleanField')()),
            ('less_than_2_weeks_before_eloping', self.gf('django.db.models.fields.BooleanField')()),
            ('between_2_12_weeks_before_eloping', self.gf('django.db.models.fields.BooleanField')()),
            ('caste_not_same_as_relative', self.gf('django.db.models.fields.BooleanField')()),
            ('caught_in_lie', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'dataentry', ['InterceptionRecord'])


    def backwards(self, orm):
        # Deleting model 'Account'
        db.delete_table(u'dataentry_account')

        # Removing M2M table for field groups on 'Account'
        db.delete_table(db.shorten_name(u'dataentry_account_groups'))

        # Removing M2M table for field user_permissions on 'Account'
        db.delete_table(db.shorten_name(u'dataentry_account_user_permissions'))

        # Deleting model 'InterceptionRecord'
        db.delete_table(u'dataentry_interceptionrecord')


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
            'less_than_2_weeks_before_eloping': ('django.db.models.fields.BooleanField', [], {}),
            'married_in_past_2_8_weeks': ('django.db.models.fields.BooleanField', [], {}),
            'married_in_past_2_weeks': ('django.db.models.fields.BooleanField', [], {}),
            'meeting_someone_across_border': ('django.db.models.fields.BooleanField', [], {}),
            'seen_in_last_month_in_nepal': ('django.db.models.fields.BooleanField', [], {}),
            'traveling_with_someone_not_with_her': ('django.db.models.fields.BooleanField', [], {}),
            'who_in_group': ('django.db.models.fields.IntegerField', [], {}),
            'wife_under_18': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['dataentry']