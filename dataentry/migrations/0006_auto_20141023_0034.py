# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0005_auto_20141007_0547'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='victiminterviewlocationbox',
        #     name='district_geocodelocation',
        # ),
        # migrations.RemoveField(
        #     model_name='victiminterviewlocationbox',
        #     name='vdc_geocodelocation',
        # ),
        migrations.AlterField(
            model_name='interceptee',
            name='district',
            field=models.ForeignKey(to='dataentry.District'),
        ),
        migrations.AlterField(
            model_name='interceptee',
            name='vdc',
            field=models.ForeignKey(to='dataentry.VDC'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address_district',
            field=models.ForeignKey(related_name=b'victim_address_district', to='dataentry.District'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address_vdc',
            field=models.ForeignKey(related_name=b'victim_address_vdc', to='dataentry.VDC'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_guardian_address_district',
            field=models.ForeignKey(to='dataentry.District'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_guardian_address_vdc',
            field=models.ForeignKey(to='dataentry.VDC'),
        ),
        migrations.AlterField(
            model_name='victiminterviewlocationbox',
            name='district',
            field=models.ForeignKey(to='dataentry.District'),
        ),
        migrations.AlterField(
            model_name='victiminterviewlocationbox',
            name='vdc',
            field=models.ForeignKey(to='dataentry.VDC'),
        ),
        migrations.AlterField(
            model_name='victiminterviewpersonbox',
            name='address_district',
            field=models.ForeignKey(to='dataentry.District'),
        ),
        migrations.AlterField(
            model_name='victiminterviewpersonbox',
            name='address_vdc',
            field=models.ForeignKey(to='dataentry.VDC'),
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='political_party_umn',
        ),
        migrations.AddField(
            model_name='victiminterviewpersonbox',
            name='political_party_uml',
            field=models.BooleanField(default=False, verbose_name=b'UML'),
            preserve_default=True,
        ),
    ]
