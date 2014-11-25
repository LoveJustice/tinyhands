# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_borderstationbudgetcalculation_travel_plus_other'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borderstationbudgetcalculation',
            name='form_entered_by',
        ),
        migrations.RemoveField(
            model_name='borderstationbudgetcalculation',
            name='form_updated_by',
        ),
    ]
