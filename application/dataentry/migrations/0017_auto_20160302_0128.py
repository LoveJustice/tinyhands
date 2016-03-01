# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0016_auto_20160301_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='level',
            field=models.CharField(default=b'district', max_length=255, choices=[(b'state', b'State'), (b'country', b'Country'), (b'city', b'City'), (b'district', b'District'), (b'vdc', b'VDC')]),
            preserve_default=True,
        ),
    ]
