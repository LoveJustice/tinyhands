# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0028_auto_20160221_0004'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=255)),
                ('gender', models.CharField(blank=True, max_length=4, choices=[(b'f', b'F'), (b'm', b'M')])),
                ('age', models.PositiveIntegerField(null=True, blank=True)),
                ('phone_contact', models.CharField(max_length=255, blank=True)),
                ('address1', models.ForeignKey(blank=True, to='dataentry.Address1', null=True)),
                ('address2', models.ForeignKey(blank=True, to='dataentry.Address2', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        # migrations.AddField(model_name="Interceptee", name='person_tmp_name', field=models.ForeignKey(to='dataentry.Person', null=True)),
        # migrations.AddField(model_name="VictimInterview", name='person_tmp_name', field=models.ForeignKey(to='dataentry.Person', null=True)),
        # migrations.AddField(model_name="VictimInterviewPersonBox", name='person_tmp_name', field=models.ForeignKey(to='dataentry.Person', null=True)),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='address1',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='address2',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='age',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='full_name',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='gender',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='phone_contact',
        # ),
        # migrations.RemoveField(
        #     model_name='interceptee',
        #     name='photo',
        # ),
        # migrations.AddField(
        #     model_name='interceptee',
        #     name='person',
        #     field=models.ForeignKey(related_name='interceptee', blank=True, to='dataentry.Person', null=True),
        #     preserve_default=True,
        # ),
    ]
