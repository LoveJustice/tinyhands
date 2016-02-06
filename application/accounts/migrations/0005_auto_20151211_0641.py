# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151015_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultpermissionsset',
            name='permission_budget_manage',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
