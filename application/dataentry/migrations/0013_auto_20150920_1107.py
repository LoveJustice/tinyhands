# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0012_borderstation_closed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borderstation',
            name='closed',
        ),
        migrations.AddField(
            model_name='borderstation',
            name='open',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
