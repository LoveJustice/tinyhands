# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DefaultPermissionsSet'
        db.create_table(u'accounts_defaultpermissionsset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission_irf_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_irf_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_irf_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'accounts', ['DefaultPermissionsSet'])

        # Adding model 'Account'
        db.create_table(u'accounts_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('permission_irf_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_irf_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_irf_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_vif_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_add', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('permission_accounts_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'accounts', ['Account'])

        # Adding M2M table for field groups on 'Account'
        m2m_table_name = db.shorten_name(u'accounts_account_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm[u'accounts.account'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['account_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'Account'
        m2m_table_name = db.shorten_name(u'accounts_account_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('account', models.ForeignKey(orm[u'accounts.account'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['account_id', 'permission_id'])


    def backwards(self, orm):
        # Deleting model 'DefaultPermissionsSet'
        db.delete_table(u'accounts_defaultpermissionsset')

        # Deleting model 'Account'
        db.delete_table(u'accounts_account')

        # Removing M2M table for field groups on 'Account'
        db.delete_table(db.shorten_name(u'accounts_account_groups'))

        # Removing M2M table for field user_permissions on 'Account'
        db.delete_table(db.shorten_name(u'accounts_account_user_permissions'))


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
            'permission_accounts_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_irf_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_vif_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'accounts.defaultpermissionsset': {
            'Meta': {'object_name': 'DefaultPermissionsSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission_accounts_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        }
    }

    complete_apps = ['accounts']