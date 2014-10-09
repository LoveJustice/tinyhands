# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20141007_0624'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alert',
            old_name='accounts',
            new_name='permissions_group',
        ),
    ]
