# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-12-07 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0207_auto_20211119_1807'),
    ]

    operations = [
        migrations.AddField(
            model_name='irfcommon',
            name='vulnerability_meeting_someone_met_online',
            field=models.BooleanField(default=False, verbose_name='Going to meet someone they met online'),
        ),
        migrations.AddField(
            model_name='irfcommon',
            name='vulnerability_travel_arranged_by_other',
            field=models.BooleanField(default=False, verbose_name='Transportation arranged by someone else'),
        ),
    ]