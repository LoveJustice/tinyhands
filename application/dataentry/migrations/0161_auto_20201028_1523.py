# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-28 15:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0160_auto_20201027_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='irfcommon',
            name='logbook_first_verification_name',
            field=models.CharField(blank=True, max_length=127),
        ),
        migrations.AddField(
            model_name='irfcommon',
            name='logbook_second_verification_name',
            field=models.CharField(blank=True, max_length=127),
        ),
    ]
