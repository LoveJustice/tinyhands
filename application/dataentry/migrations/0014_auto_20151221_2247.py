# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0013_auto_20150920_1107'),
    ]

    operations = [
        migrations.RenameField("VDC","cannonical_name", "canonical_name")
    ]
