# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_defaultpermissionsset_permission_vdc_manage'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='permission_vdc_manage',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
