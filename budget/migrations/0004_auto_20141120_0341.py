# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0003_auto_20141119_0224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borderstationbudgetcalculation',
            name='communication_manager_amount',
            field=models.PositiveIntegerField(default=1000, verbose_name=b'for manager'),
        ),
    ]
