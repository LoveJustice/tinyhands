# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20150918_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultpermissionsset',
            name='permission_budget_manage',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
