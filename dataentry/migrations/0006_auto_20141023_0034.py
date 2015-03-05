# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import chain

from django.db import models, migrations

def migrate_foreign_keys(app_config, app_name, model_name, district_field_name, vdc_field_name):
    model = app_config.get_model(app_name, model_name)
    District = app_config.get_model(app_name, 'District')
    VDC = app_config.get_model(app_name, 'VDC')

    for instance in model.objects.all():
        district_name = getattr(instance, district_field_name)
        if len(district_name) > 0:
            district, created = District.objects.get_or_create(name=district_name)
            instance.district_tmp = district
        vdc_name = getattr(instance, vdc_field_name)
        if len(vdc_name) > 0:
            vdc, created = VDC.objects.get_or_create(name=vdc_name, latitude=0.0, longitude=0.0, district=district)
            instance.vdc_tmp = vdc
        instance.save()

def migration_ops(model_name, district_field_name, vdc_field_name):
    return [
        migrations.AddField(model_name=model_name, name='district_tmp',
                            field=models.ForeignKey(to='dataentry.District', null=True)),
        migrations.AddField(model_name=model_name, name='vdc_tmp',
                            field=models.ForeignKey(to='dataentry.VDC', null=True)),

        migrations.RunPython(lambda app, schema_editor: migrate_foreign_keys(app, 'dataentry',
                                                                             model_name,
                                                                             district_field_name,
                                                                             vdc_field_name)),

        migrations.RemoveField(model_name=model_name, name=district_field_name),
        migrations.RenameField(model_name=model_name, old_name='district_tmp', new_name=district_field_name),

        migrations.RemoveField(model_name=model_name, name=vdc_field_name),
        migrations.RenameField(model_name=model_name, old_name='vdc_tmp', new_name=vdc_field_name),
    ]

class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0005_auto_20141007_0547'),
    ]

    operations = chain(migration_ops('interceptee', 'district', 'vdc'),
                       migration_ops('victiminterviewlocationbox', 'district', 'vdc'),
                       migration_ops('victiminterviewpersonbox', 'address_district', 'address_vdc'),
                       migration_ops('victiminterview', 'victim_address_district', 'victim_address_vdc'),
                       migration_ops('victiminterview',
                                     'victim_guardian_address_district', 'victim_guardian_address_vdc'),
                       [ migrations.RemoveField(model_name='victiminterviewpersonbox',
                                                name='political_party_umn'),
                         migrations.AddField(model_name='victiminterviewpersonbox',
                                             name='political_party_uml',
                                             field=models.BooleanField(default=False, verbose_name=b'UML'),
                                             preserve_default=True) ])
