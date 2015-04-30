# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20141107_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='permission_budget_manage',
            field=models.BooleanField(default=False),
        ),
    ]
