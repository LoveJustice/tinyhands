# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0019_auto_20160220_0825'),
    ]

    operations = [
        migrations.RenameField('VictimInterview', 'victim_guardian_address_district', 'victim_guardian_address1'),
    ]
