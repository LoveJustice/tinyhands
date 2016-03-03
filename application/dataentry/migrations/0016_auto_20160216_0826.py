# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0015_auto_20160216_0151'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VDC',
            new_name='Address2',
        ),
    ]
