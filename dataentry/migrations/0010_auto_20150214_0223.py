# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0009_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borderstation',
            name='station_code',
            field=models.CharField(unique=True, max_length=3),
            preserve_default=True,
        ),
    ]
