# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_permission_receive_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='defaultpermissionsset',
            name='permission_receive_email',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
