# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0007_borderstation'),
    ]

    operations = [
        migrations.AddField(
            model_name='borderstation',
            name='date_established',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='borderstation',
            name='has_shelter',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='borderstation',
            name='latitude',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='borderstation',
            name='longitude',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
    ]
