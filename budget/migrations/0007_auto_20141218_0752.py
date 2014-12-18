# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_auto_20141123_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='cost',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
