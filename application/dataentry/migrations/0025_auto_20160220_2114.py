# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0024_auto_20160220_2102'),
    ]

    operations = [
        migrations.RenameField('VictimInterview', 'victim_address_vdc', 'victim_address2'),
        migrations.RenameField('VictimInterview', 'victim_guardian_address_vdc', 'victim_guardian_address2'),
    ]
