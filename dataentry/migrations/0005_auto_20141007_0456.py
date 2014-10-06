# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0004_auto_20141002_0455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interceptionrecord',
            name='has_signature',
            field=models.BooleanField(default=False, verbose_name=b'Scanned form has signature?'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='has_signature',
            field=models.BooleanField(default=False, verbose_name=b'Scanned form has signature'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_knew_details_about_destination',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_recruited_in_village',
            field=models.BooleanField(default=b'False', verbose_name=b'Did someone recruit you in your village and persuade you to abroad?'),
        ),
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_stayed_somewhere_between',
            field=models.BooleanField(default=False),
        ),
    ]
