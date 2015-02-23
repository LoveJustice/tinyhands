# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0013_auto_20141205_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='canonical_vdc',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.VDC', null=True),
        ),
    ]
