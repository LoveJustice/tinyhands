# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20151211_0641'),
    ]

    operations = [
        migrations.RenameField('DefaultPermissionsSet', 'permission_vdc_manage', 'permission_address2_manage'),
        migrations.RenameField('Account', 'permission_vdc_manage', 'permission_address2_manage'),
    ]
