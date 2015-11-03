# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20150925_0211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='otherbudgetitemcost',
            name='form_section',
            field=models.IntegerField(null=True, verbose_name=[(1, b'Travel'), (2, b'Miscellaneous'), (3, b'Awareness'), (4, b'Supplies'), (5, b'Shelter'), (6, b'FoodGas'), (7, b'Communication'), (8, b'Staff')], blank=True),
            preserve_default=True,
        ),
    ]
