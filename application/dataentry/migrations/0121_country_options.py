# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-11-11 19:37
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0120_auto_20191105_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='options',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
