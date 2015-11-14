# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0001_initial'),
        ('budget', '0001_initial'),
        ('static_border_stations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='staffsalary',
            name='staff_person',
            field=models.ForeignKey(blank=True, to='static_border_stations.Staff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='otherbudgetitemcost',
            name='budget_item_parent',
            field=models.ForeignKey(blank=True, to='budget.BorderStationBudgetCalculation', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='borderstationbudgetcalculation',
            name='border_station',
            field=models.ForeignKey(to='dataentry.BorderStation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='borderstationbudgetcalculation',
            name='members',
            field=models.ManyToManyField(to='static_border_stations.Staff', through='budget.StaffSalary'),
            preserve_default=True,
        ),
    ]
