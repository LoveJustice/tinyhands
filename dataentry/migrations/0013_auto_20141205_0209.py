# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0012_auto_20141119_0530'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='canonical_district',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='canonical_vdc',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.District', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='canonical_age',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.Age', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='canonical_name',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.Name', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='canonical_phone',
            field=models.ForeignKey(related_name=b'+', blank=True, to='dataentry.Phone', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(blank=True, max_length=6, choices=[(b'female', b'Female'), (b'male', b'Male')]),
        ),
    ]
