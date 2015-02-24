# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='victiminterview',
            name='victim_address_district',
            field=models.ForeignKey(related_name=b'victim_address_district', default=1, to='dataentry.District'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='victiminterview',
            name='victim_address_vdc',
            field=models.ForeignKey(related_name=b'victim_address_vdc', default=1, to='dataentry.VDC'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='victiminterviewpersonbox',
            name='address_district',
            field=models.ForeignKey(default=1, to='dataentry.District'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='victiminterviewpersonbox',
            name='address_vdc',
            field=models.ForeignKey(default=1, to='dataentry.VDC'),
            preserve_default=False,
        ),
    ]
