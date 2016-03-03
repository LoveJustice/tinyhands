# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0018_auto_20160304_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='district',
            name='level',
            field=models.CharField(default=b'district', max_length=255, choices=[(b'State', b'State'), (b'Country', b'Country'), (b'City', b'City'), (b'District', b'District'), (b'VDC', b'VDC'), (b'Building', b'Building'), (b'Block', b'Block')]),
            preserve_default=True,
        ),
    ]
