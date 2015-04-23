# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0006_auto_20141119_0232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='salary',
        ),
    ]
