# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0010_auto_20150214_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interceptee',
            name='district',
            field=models.ForeignKey(blank=True, to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='interceptee',
            name='vdc',
            field=models.ForeignKey(blank=True, to='dataentry.VDC', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address_district',
            field=models.ForeignKey(related_name='victim_address_district', to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address_vdc',
            field=models.ForeignKey(related_name='victim_address_vdc', to='dataentry.VDC', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterviewlocationbox',
            name='district',
            field=models.ForeignKey(to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterviewlocationbox',
            name='vdc',
            field=models.ForeignKey(to='dataentry.VDC', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterviewpersonbox',
            name='address_district',
            field=models.ForeignKey(to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='victiminterviewpersonbox',
            name='address_vdc',
            field=models.ForeignKey(to='dataentry.VDC', null=True),
            preserve_default=True,
        ),
    ]
