# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-07-11 14:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0103_auto_20190708_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='mdf_sender_email',
            field=models.CharField(default='support@dreamsuite.org', max_length=127),
            preserve_default=False,
        ),
    ]