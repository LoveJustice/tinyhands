# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0008_auto_20141031_0111'),
        ('static_border_stations', '0002_auto_20141105_0227'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommitteeMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('receives_money_distribution_form', models.BooleanField(default=False)),
                ('border_station', models.ForeignKey(default=1, to='dataentry.BorderStation')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('receives_money_distribution_form', models.BooleanField(default=False)),
                ('border_station', models.ForeignKey(default=1, to='dataentry.BorderStation')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='person',
            name='border_station',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]
