# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0009_borderstationbudgetcalculation_month_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borderstationbudgetcalculation',
            name='month_year',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 5, 22, 49, 36, 624223)),
            preserve_default=True,
        ),
    ]
