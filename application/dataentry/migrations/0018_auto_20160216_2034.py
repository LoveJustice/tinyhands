# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0017_auto_20160216_2002'),
    ]

    operations = [
        migrations.RenameField('Interceptee', 'district', 'address1'),
    ]
