from __future__ import unicode_literals

from django.db import models, migrations

from models.py import NullableEmailField

class Migration(migrations.Migration):

    dependencies = [
        ('static_border_stations', '0003_auto_20141112_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Person',
            name='email',
            field=NullableEmailField(blank=True, null=True, default=None, unique=True),
        ),
        migrations.AlterField(
            model_name='Staff',
            name='email',
            field=NullableEmailField(blank=True, null=True, default=None, unique=True),
        ),
        migrations.AlterField(
            model_name='CommitteeMember',
            name='email',
            field=NullableEmailField(blank=True, null=True, default=None, unique=True),
        ),
    ]