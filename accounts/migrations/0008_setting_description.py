# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_setting'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='description',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
