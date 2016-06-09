# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0028_auto_20160221_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuzzyMatching',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1_cutoff', models.PositiveIntegerField(default=0)),
                ('address1_limit', models.PositiveIntegerField(default=0)),
                ('address2_cutoff', models.PositiveIntegerField(default=0)),
                ('address2_limit', models.PositiveIntegerField(default=0)),
                ('person_cutoff', models.PositiveIntegerField(default=0)),
                ('person_limit', models.PositiveIntegerField(default=0)),
                ('phone_number_cutoff', models.PositiveIntegerField(default=0)),
                ('phone_number_limit', models.PositiveIntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
