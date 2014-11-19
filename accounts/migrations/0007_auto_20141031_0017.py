# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_defaultpermissionsset_permission_receive_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='permission_border_stations_add',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='permission_border_stations_edit',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='permission_border_stations_view',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_border_stations_add',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_border_stations_edit',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_border_stations_view',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
