# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0007_remove_staff_salary'),
        ('budget', '0007_auto_20141218_0752'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffSalary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salary', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('budget_calc_sheet', models.ForeignKey(blank=True, to='budget.BorderStationBudgetCalculation', null=True)),
                ('staff_person', models.ForeignKey(blank=True, to='static_border_stations.Staff', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='borderstationbudgetcalculation',
            name='members',
            field=models.ManyToManyField(to='static_border_stations.Staff', through='budget.StaffSalary'),
            preserve_default=True,
        ),
    ]
