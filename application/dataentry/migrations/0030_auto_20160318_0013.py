# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0029_fuzzymatching'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuzzymatching',
            name='address1_cutoff',
            field=models.PositiveIntegerField(default=70),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuzzymatching',
            name='address1_limit',
            field=models.PositiveIntegerField(default=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuzzymatching',
            name='address2_cutoff',
            field=models.PositiveIntegerField(default=70),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuzzymatching',
            name='address2_limit',
            field=models.PositiveIntegerField(default=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuzzymatching',
            name='person_cutoff',
            field=models.PositiveIntegerField(default=90),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='fuzzymatching',
            name='person_limit',
            field=models.PositiveIntegerField(default=10),
            preserve_default=True,
        ),
    ]
