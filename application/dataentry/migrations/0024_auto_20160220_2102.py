# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0023_auto_20160220_0916'),
    ]

    operations = [
        migrations.RenameField('Interceptee', 'vdc', 'address2'),
    ]
