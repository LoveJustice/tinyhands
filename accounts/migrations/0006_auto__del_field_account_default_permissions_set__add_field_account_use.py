# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Account.default_permissions_set'
        db.delete_column(u'accounts_account', 'default_permissions_set_id')

        # Adding field 'Account.user_designation'
        db.add_column(u'accounts_account', 'user_designation',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='accounts', to=orm['accounts.DefaultPermissionsSet']),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Account.default_permissions_set'
        raise RuntimeError("Cannot reverse this migration. 'Account.default_permissions_set' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Account.default_permissions_set'
        db.add_column(u'accounts_account', 'default_permissions_set',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='accounts', to=orm['accounts.DefaultPermissionsSet']),
                      keep_default=False)

        # Deleting field 'Account.user_designation'
        db.delete_column(u'accounts_account', 'user_designation_id')


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
            'permission_accounts_defaults': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'permission_accounts_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permission_accounts_defaults': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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