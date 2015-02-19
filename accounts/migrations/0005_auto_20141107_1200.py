# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_account_permission_vdc_manage'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='permission_budget_manage',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_budget_manage',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
