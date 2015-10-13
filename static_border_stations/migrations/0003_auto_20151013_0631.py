# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0002_auto_20151009_0201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committeemember',
            name='border_station',
            field=models.ForeignKey(default=1, to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='border_station',
            field=models.ForeignKey(default=1, to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='border_station',
            field=models.ForeignKey(default=1, to='dataentry.BorderStation', null=True),
            preserve_default=True,
        ),
    ]
