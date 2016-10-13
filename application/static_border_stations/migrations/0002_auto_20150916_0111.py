# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import static_border_stations.models


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committeemember',
            name='email',
            field=static_border_stations.models.NullableEmailField(default=None, max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='staff',
            name='email',
            field=static_border_stations.models.NullableEmailField(default=None, max_length=75, null=True, blank=True),
            preserve_default=True,
        ),
    ]
