# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0027_auto_20160221_0001'),
    ]

    operations = [
        migrations.RenameField('VictimInterviewLocationBox', 'vdc', 'address2'),
    ]
