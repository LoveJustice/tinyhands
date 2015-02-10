# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0008_auto_20141031_0111'),
        ('static_border_stations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='border_station',
            field=models.ForeignKey(default=1, to='dataentry.BorderStation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='border_station',
            field=models.ForeignKey(default=1, to='dataentry.BorderStation'),
            preserve_default=True,
        ),
    ]
