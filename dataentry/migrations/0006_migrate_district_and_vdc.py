# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import chain

from django.core.management import call_command
from django.db import models, migrations

def load_fixture(fixture_name):
    call_command('loaddata', fixture_name, app_label='dataentry')

def migrate_foreign_keys(app_config, app_name, model_name, district_field_name, vdc_field_name):
    model = app_config.get_model(app_name, model_name)
    District = app_config.get_model(app_name, 'District')
    VDC = app_config.get_model(app_name, 'VDC')

    for instance in model.objects.all():
        district_name = getattr(instance, district_field_name).strip()
        if len(district_name) > 0:
            district, created = District.objects.get_or_create(name=district_name)
            instance.district_tmp = district
        vdc_name = getattr(instance, vdc_field_name)
        if len(vdc_name) > 0:
            vdc, created = VDC.objects.get_or_create(name=vdc_name, latitude=0.0, longitude=0.0,
                                                     district=district)
            instance.vdc_tmp = vdc
        instance.save()

def migration_ops(model_name, district_field_name, vdc_field_name):
    return [
        # Add temporary fields to store the new foreign keys.
        migrations.AddField(model_name=model_name, name='district_tmp',
                            field=models.ForeignKey(to='dataentry.District', null=True)),
        migrations.AddField(model_name=model_name, name='vdc_tmp',
                            field=models.ForeignKey(to='dataentry.VDC', null=True)),

        # Set values for the temporary fields.
        migrations.RunPython(lambda app, schema_editor:
                             migrate_foreign_keys(app, 'dataentry', model_name,
                                                  district_field_name, vdc_field_name)),

        # Replace the old fields with the new ones.
        migrations.RemoveField(model_name=model_name, name=district_field_name),
        migrations.RenameField(model_name=model_name, old_name='district_tmp', new_name=district_field_name),

        migrations.RemoveField(model_name=model_name, name=vdc_field_name),
        migrations.RenameField(model_name=model_name, old_name='vdc_tmp', new_name=vdc_field_name),
    ]

class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0005_auto_20141007_0547'),
    ]

    operations = chain(
        [
            # Moved this up from a later migration in order to allow fixtures to be loaded.
            migrations.AddField(model_name='vdc', name='verified',
                                field=models.BooleanField(default=False), preserve_default=True,),

            # Load the fixtures so that the following operations can use them.
            migrations.RunPython(lambda app, se: load_fixture('district')),
            migrations.RunPython(lambda app, se: load_fixture('vdc'))
        ],

        # Migrate all the VDC and District fields from strings to foreign-key references.
        migration_ops('interceptee', 'district', 'vdc'),
        migration_ops('victiminterviewlocationbox', 'district', 'vdc'),
        migration_ops('victiminterviewpersonbox', 'address_district', 'address_vdc'),
        migration_ops('victiminterview', 'victim_address_district', 'victim_address_vdc'),
        migration_ops('victiminterview', 'victim_guardian_address_district', 'victim_guardian_address_vdc'),

        # Other stuff that was originally the content of this migration.
        [ migrations.RemoveField(model_name='victiminterviewpersonbox',
                                 name='political_party_umn'),
          migrations.AddField(model_name='victiminterviewpersonbox',
                              name='political_party_uml',
                              field=models.BooleanField(default=False, verbose_name=b'UML'),
                              preserve_default=True) ]
    )
