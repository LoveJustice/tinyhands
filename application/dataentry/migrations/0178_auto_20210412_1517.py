# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2021-04-12 15:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0177_auto_20210406_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='legalcase',
            name='location',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='legalcase',
            name='human_trafficking',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunSQL("update dataentry_legalcase set human_trafficking='Yes' where human_trafficking='true'"),
        migrations.RunSQL("update dataentry_legalcase set human_trafficking=null where human_trafficking='false'"),
        migrations.RunSQL("update dataentry_legalcase set missing_data_count=missing_data_count+1 where (human_trafficking is null or human_trafficking = '') and missing_data_count is not null"),
        migrations.RunSQL("update dataentry_legalcase set missing_data_count=missing_data_count+1 where (police_case is null or police_case = '') and missing_data_count is not null"),
        migrations.RunSQL("update dataentry_legalcase set missing_data_count=missing_data_count+1 where missing_data_count is not null"), # for location
    ]