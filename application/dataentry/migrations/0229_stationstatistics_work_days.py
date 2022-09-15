# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2022-07-08 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0228_auto_20220707_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='stationstatistics',
            name='work_days',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunSQL('update dataentry_stationstatistics set work_days=21'),
        migrations.RunSQL('update dataentry_locationstaff set work_fraction = work_fraction * 21'),
    ]