# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0020_auto_20160220_0840'),
    ]

    operations = [
        migrations.RenameField('VictimInterviewPersonBox', 'address_district', 'address1'),
    ]
