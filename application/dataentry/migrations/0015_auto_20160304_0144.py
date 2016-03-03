# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0014_auto_20151221_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='district',
            name='completed',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='district',
            name='latitude',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='district',
            name='level',
            field=models.CharField(default=b'District', max_length=255, choices=[(b'State', b'State'), (b'Country', b'Country'), (b'City', b'City'), (b'District', b'District'), (b'VDC', b'VDC'), (b'Building', b'Building'), (b'Block', b'Block')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='district',
            name='longitude',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
