# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2021-09-09 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0195_auto_20210902_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='irfcommon',
            name='control_connected_known_trafficker',
            field=models.BooleanField(default=False, verbose_name='Is connected to a known trafficker'),
        ),
        migrations.AddField(
            model_name='irfcommon',
            name='flight_number',
            field=models.CharField(max_length=127, null=True),
        ),
        migrations.AlterField(
            model_name='irfcommon',
            name='control_status_known_trafficker',
            field=models.BooleanField(default=False, verbose_name='Is a known trafficker'),
        ),
    ]
