# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-24 07:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0061_merge_20180817_0743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irfnepal',
            name='noticed_on_train',
        ),
        migrations.AddField(
            model_name='irfnepal',
            name='noticed_walking_to_border',
            field=models.BooleanField(default=False, verbose_name='Walking to border'),
        ),
    ]