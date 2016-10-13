# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20151013_0324'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='permission_border_stations_delete',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_border_stations_delete',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='defaultpermissionsset',
            name='permission_budget_manage',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
