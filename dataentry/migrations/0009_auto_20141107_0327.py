# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0008_auto_20141031_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='canonical_age',
            field=models.ForeignKey(related_name=b'+', to='dataentry.Age'),
        ),
        migrations.AlterField(
            model_name='person',
            name='canonical_name',
            field=models.ForeignKey(related_name=b'+', to='dataentry.Name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='canonical_phone',
            field=models.ForeignKey(related_name=b'+', to='dataentry.Phone'),
        ),
    ]
