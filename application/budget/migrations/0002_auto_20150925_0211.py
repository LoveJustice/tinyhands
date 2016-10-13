# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='form_section',
            field=models.IntegerField(null=True, verbose_name=[(1, b'Travel'), (2, b'Miscellaneous'), (3, b'Awareness'), (4, b'Supplies'), (5, b'Shelter'), (6, b'FoodGas'), (7, b'Communication')], blank=True),
            preserve_default=True,
        ),
    ]
