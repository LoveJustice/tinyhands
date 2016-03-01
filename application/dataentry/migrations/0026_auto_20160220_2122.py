# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0025_auto_20160220_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address2',
            field=models.ForeignKey(related_name='victim_address2', to='dataentry.Address2', null=True),
            preserve_default=True,
        ),
    ]
