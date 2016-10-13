# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0002_auto_20150916_0111'),
    ]

    operations = [
        migrations.AddField(
            model_name='committeemember',
            name='phone',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='committeemember',
            name='position',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='phone',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='staff',
            name='position',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='border_station',
            field=models.ForeignKey(to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='border_station',
            field=models.ForeignKey(to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='border_station',
            field=models.ForeignKey(to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
    ]
