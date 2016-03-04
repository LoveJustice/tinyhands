# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0016_auto_20160216_0826'),
    ]

    operations = [
        migrations.RenameField('Address2', 'district', 'address1'),
    ]
