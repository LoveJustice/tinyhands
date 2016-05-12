# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0030_auto_20160309_0104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address2',
            name='name',
            field=models.CharField(default=b'Unknown', max_length=255),
            preserve_default=True,
        ),
    ]
