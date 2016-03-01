# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0018_auto_20160216_2034'),
    ]

    operations = [
        migrations.RenameField('VictimInterview', 'victim_address_district', 'victim_address1'),
    ]
