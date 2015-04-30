# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_auto_20141120_0341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='budget_item_parent',
            field=models.ForeignKey(to='budget.BorderStationBudgetCalculation', blank=True),
        ),
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='form_section',
            field=models.IntegerField(verbose_name=[(1, b'Travel'), (2, b'Miscellaneous'), (3, b'Awareness'), (4, b'Supplies')], blank=True),
        ),
    ]
