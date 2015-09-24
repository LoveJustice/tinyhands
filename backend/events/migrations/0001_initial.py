# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250, verbose_name=b'Title')),
                ('location', models.CharField(max_length=250, verbose_name=b'Location', blank=True)),
                ('start_date', models.DateField(verbose_name=b'Start Date')),
                ('start_time', models.TimeField(null=True, verbose_name=b'Start Time')),
                ('end_date', models.DateField(verbose_name=b'End Date')),
                ('end_time', models.TimeField(null=True, verbose_name=b'End Time')),
                ('description', models.TextField(verbose_name=b'Description', blank=True)),
                ('is_repeat', models.BooleanField(default=False, verbose_name=b'Repeat')),
                ('repetition', models.CharField(default=b'', max_length=50, blank=True, choices=[(b'D', b'Daily'), (b'W', b'Weekly'), (b'M', b'Monthly')])),
                ('ends', models.DateField(null=True, verbose_name=b'Ends At', blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name=b'Crated on', null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, verbose_name=b'Crated on', null=True)),
            ],
            options={
                'verbose_name_plural': 'Event',
            },
            bases=(models.Model,),
        ),
    ]
