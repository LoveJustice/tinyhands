# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Events',
            new_name='Event',
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name_plural': 'Event'},
        ),
    ]
