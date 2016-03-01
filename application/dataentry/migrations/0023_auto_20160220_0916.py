# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0022_auto_20160220_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='victiminterview',
            name='victim_address1',
            field=models.ForeignKey(related_name='victim_address1', to='dataentry.Address1', null=True),
            preserve_default=True,
        ),
    ]
