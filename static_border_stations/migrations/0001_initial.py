# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import static_border_stations.models


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommitteeMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', static_border_stations.models.NullableEmailField(default=None, max_length=75, null=True, blank=True)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('position', models.CharField(max_length=255, null=True, blank=True)),
                ('receives_money_distribution_form', models.BooleanField(default=False)),
                ('border_station', models.ForeignKey(to='dataentry.BorderStation', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('latitude', models.FloatField(null=True)),
                ('longitude', models.FloatField(null=True)),
                ('border_station', models.ForeignKey(to='dataentry.BorderStation', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', static_border_stations.models.NullableEmailField(default=None, max_length=75, null=True, blank=True)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('phone', models.CharField(max_length=255, null=True, blank=True)),
                ('position', models.CharField(max_length=255, null=True, blank=True)),
                ('receives_money_distribution_form', models.BooleanField(default=False)),
                ('border_station', models.ForeignKey(to='dataentry.BorderStation', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
