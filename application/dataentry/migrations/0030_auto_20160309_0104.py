# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0029_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='address2',
            name='level',
            field=models.CharField(default=b'VDC', max_length=255, choices=[(b'State', b'State'), (b'Country', b'Country'), (b'City', b'City'), (b'District', b'District'), (b'VDC', b'VDC'), (b'Building', b'Building'), (b'Block', b'Block')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address2',
            name='latitude',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address2',
            name='longitude',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
    ]
