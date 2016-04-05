# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0021_auto_20160220_0847'),
    ]

    operations = [
        migrations.RenameField('VictimInterviewLocationBox', 'district', 'address1'),
    ]
