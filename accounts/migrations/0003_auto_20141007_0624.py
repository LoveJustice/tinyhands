# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='accounts',
            field=models.ManyToManyField(to=b'accounts.DefaultPermissionsSet'),
        ),
    ]
