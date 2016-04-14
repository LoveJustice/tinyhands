# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0026_auto_20160220_2122'),
    ]

    operations = [
        migrations.RenameField('VictimInterviewPersonBox', 'address_vdc', 'address2'),
    ]
