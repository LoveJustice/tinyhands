# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_auto_20141123_0524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='budget_item_parent',
            field=models.ForeignKey(blank=True, to='budget.BorderStationBudgetCalculation', null=True),
        ),
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='form_section',
            field=models.IntegerField(null=True, verbose_name=[(1, b'Travel'), (2, b'Miscellaneous'), (3, b'Awareness'), (4, b'Supplies')], blank=True),
        ),
    ]
