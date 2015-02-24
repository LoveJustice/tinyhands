# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0007_auto_20141025_2232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='district',
        ),
        migrations.RemoveField(
            model_name='person',
            name='vdc',
        ),
        migrations.AddField(
            model_name='person',
            name='districts',
            field=models.ManyToManyField(related_name=b'+', to='dataentry.District'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='vdcs',
            field=models.ManyToManyField(related_name=b'+', to='dataentry.VDC'),
            preserve_default=True,
        ),
    ]
