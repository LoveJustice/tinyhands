# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0014_auto_20151221_2247'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='District',
            new_name='Address1',
        ),
    ]
