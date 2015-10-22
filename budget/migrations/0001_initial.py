# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0001_initial'),
        ('static_border_stations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BorderStationBudgetCalculation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time_entered', models.DateTimeField(auto_now_add=True)),
                ('date_time_last_updated', models.DateTimeField(auto_now=True)),
                ('month_year', models.DateTimeField(default=datetime.datetime.now)),
                ('communication_chair', models.BooleanField(default=False)),
                ('communication_chair_amount', models.PositiveIntegerField(default=1000, verbose_name=b'for chair')),
                ('communication_manager', models.BooleanField(default=False)),
                ('communication_manager_amount', models.PositiveIntegerField(default=1000, verbose_name=b'for manager')),
                ('communication_number_of_staff_with_walkie_talkies', models.PositiveIntegerField(default=0, verbose_name=b'# of staff with walkie-talkies')),
                ('communication_number_of_staff_with_walkie_talkies_multiplier', models.PositiveIntegerField(default=100)),
                ('communication_each_staff', models.PositiveIntegerField(default=0, verbose_name=b'each staff')),
                ('communication_each_staff_multiplier', models.PositiveIntegerField(default=300)),
                ('travel_chair_with_bike', models.BooleanField(default=False)),
                ('travel_chair_with_bike_amount', models.PositiveIntegerField(default=2000, verbose_name=b'for chair (if has bike)')),
                ('travel_manager_with_bike', models.BooleanField(default=False)),
                ('travel_manager_with_bike_amount', models.PositiveIntegerField(default=2000, verbose_name=b'for manager (if has bike)')),
                ('travel_number_of_staff_using_bikes', models.PositiveIntegerField(default=0, verbose_name=b'# of staff using bikes')),
                ('travel_number_of_staff_using_bikes_multiplier', models.PositiveIntegerField(default=1000)),
                ('travel_last_months_expense_for_sending_girls_home', models.PositiveIntegerField(default=0)),
                ('travel_motorbike', models.BooleanField(default=False, verbose_name=b'Motorbike')),
                ('travel_motorbike_amount', models.PositiveIntegerField(default=60000)),
                ('travel_plus_other', models.PositiveIntegerField(default=0)),
                ('administration_number_of_intercepts_last_month', models.PositiveIntegerField(default=0, verbose_name=b'# of intercepts last month')),
                ('administration_number_of_intercepts_last_month_multiplier', models.PositiveIntegerField(default=20)),
                ('administration_number_of_intercepts_last_month_adder', models.PositiveIntegerField(default=1000)),
                ('administration_number_of_meetings_per_month', models.PositiveIntegerField(default=0, verbose_name=b'# of meetings per month')),
                ('administration_number_of_meetings_per_month_multiplier', models.PositiveIntegerField(default=600)),
                ('administration_booth', models.BooleanField(default=False, verbose_name=b'Booth')),
                ('administration_booth_amount', models.PositiveIntegerField(default=30000)),
                ('administration_registration', models.BooleanField(default=False, verbose_name=b'Registration')),
                ('administration_registration_amount', models.PositiveIntegerField(default=2000)),
                ('medical_last_months_expense', models.PositiveIntegerField(default=0, verbose_name=b"Last month's medical expense")),
                ('miscellaneous_number_of_intercepts_last_month', models.PositiveIntegerField(default=0, verbose_name=b'# of intercepts last month')),
                ('miscellaneous_number_of_intercepts_last_month_multiplier', models.PositiveIntegerField(default=300)),
                ('shelter_rent', models.PositiveIntegerField(default=0)),
                ('shelter_water', models.PositiveIntegerField(default=0)),
                ('shelter_electricity', models.PositiveIntegerField(default=0)),
                ('shelter_shelter_startup', models.BooleanField(default=False, verbose_name=b'Shelter Startup')),
                ('shelter_shelter_startup_amount', models.PositiveIntegerField(default=71800)),
                ('shelter_shelter_two', models.BooleanField(default=False, verbose_name=b'Shelter 2')),
                ('shelter_shelter_two_amount', models.PositiveIntegerField(default=36800)),
                ('food_and_gas_number_of_intercepted_girls', models.PositiveIntegerField(default=0, verbose_name=b'# of intercepted girls')),
                ('food_and_gas_number_of_intercepted_girls_multiplier_before', models.PositiveIntegerField(default=100)),
                ('food_and_gas_number_of_intercepted_girls_multiplier_after', models.PositiveIntegerField(default=3)),
                ('food_and_gas_limbo_girls_multiplier', models.PositiveIntegerField(default=100)),
                ('food_and_gas_number_of_limbo_girls', models.PositiveIntegerField(default=0, verbose_name=b'# of limbo girls')),
                ('food_and_gas_number_of_days', models.PositiveIntegerField(default=0, verbose_name=b'# of days')),
                ('awareness_contact_cards', models.BooleanField(default=False, verbose_name=b'Contact Cards')),
                ('awareness_contact_cards_boolean_amount', models.PositiveIntegerField(default=4000)),
                ('awareness_contact_cards_amount', models.PositiveIntegerField(default=0)),
                ('awareness_awareness_party_boolean', models.BooleanField(default=False, verbose_name=b'Awareness Party')),
                ('awareness_awareness_party', models.PositiveIntegerField(default=0)),
                ('awareness_sign_boards_boolean', models.BooleanField(default=False, verbose_name=b'Sign Boards')),
                ('awareness_sign_boards', models.PositiveIntegerField(default=0)),
                ('supplies_walkie_talkies_boolean', models.BooleanField(default=False, verbose_name=b'Walkie-talkies')),
                ('supplies_walkie_talkies_amount', models.PositiveIntegerField(default=0)),
                ('supplies_recorders_boolean', models.BooleanField(default=False, verbose_name=b'Recorders')),
                ('supplies_recorders_amount', models.PositiveIntegerField(default=0)),
                ('supplies_binoculars_boolean', models.BooleanField(default=False, verbose_name=b'Binoculars')),
                ('supplies_binoculars_amount', models.PositiveIntegerField(default=0)),
                ('supplies_flashlights_boolean', models.BooleanField(default=False, verbose_name=b'Flashlights')),
                ('supplies_flashlights_amount', models.PositiveIntegerField(default=0)),
                ('border_station', models.ForeignKey(to='dataentry.BorderStation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OtherBudgetItemCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('cost', models.PositiveIntegerField(default=0)),
                ('form_section', models.IntegerField(null=True, verbose_name=[(1, b'Travel'), (2, b'Miscellaneous'), (3, b'Awareness'), (4, b'Supplies'), (5, b'Shelter'), (6, b'FoodGas'), (7, b'Communication'), (8, b'Staff')], blank=True)),
                ('budget_item_parent', models.ForeignKey(blank=True, to='budget.BorderStationBudgetCalculation', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
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
