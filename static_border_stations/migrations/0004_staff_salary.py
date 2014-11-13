# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0003_auto_20141112_0117'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='salary',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
