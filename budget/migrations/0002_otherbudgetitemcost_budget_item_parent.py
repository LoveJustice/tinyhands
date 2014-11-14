# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='otherbudgetitemcost',
            name='budget_item_parent',
            field=models.ForeignKey(default=0, to='budget.BorderStationBudgetCalculation'),
            preserve_default=False,
        ),
    ]
