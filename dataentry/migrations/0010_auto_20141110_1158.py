# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0009_auto_20141107_0327'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='age',
            name='person',
        ),
        migrations.AddField(
            model_name='age',
            name='person',
            field=models.ManyToManyField(related_name=b'ages', to=b'dataentry.Person'),
        ),
        migrations.RemoveField(
            model_name='age',
            name='value',
        ),
        migrations.AddField(
            model_name='age',
            name='value',
            field=models.PositiveIntegerField(unique=True, null=True, verbose_name=b'age', blank=True),
        ),
    ]
