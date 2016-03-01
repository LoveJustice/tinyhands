# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0015_auto_20160226_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='completed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='district',
            name='level',
            field=models.CharField(default=b'District', max_length=255, choices=[(b'state', b'State'), (b'country', b'Country'), (b'city', b'City'), (b'district', b'District'), (b'vdc', b'VDC')]),
            preserve_default=True,
        ),
    ]
