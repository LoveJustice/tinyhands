# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20141007_0627'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='permission_receive_email',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
