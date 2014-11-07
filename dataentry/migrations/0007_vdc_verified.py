# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0006_auto_20141023_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='vdc',
            name='verified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
