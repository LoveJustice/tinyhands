# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0006_auto_20141009_0613'),
    ]

    operations = [
        migrations.CreateModel(
            name='Age',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.PositiveIntegerField(null=True, verbose_name=b'age', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=4, choices=[(b'female', b'Female'), (b'male', b'Male')])),
                ('canonical_age', models.OneToOneField(related_name=b'+', to='dataentry.Age')),
                ('canonical_name', models.OneToOneField(related_name=b'+', to='dataentry.Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255, blank=True)),
                ('person', models.ForeignKey(related_name=b'phone_numbers', to='dataentry.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='person',
            name='canonical_phone',
            field=models.OneToOneField(related_name=b'+', to='dataentry.Phone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='district',
            field=models.ManyToManyField(to='dataentry.District'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='vdc',
            field=models.ManyToManyField(to='dataentry.VDC'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='name',
            name='person',
            field=models.ForeignKey(related_name=b'names', to='dataentry.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='age',
            name='person',
            field=models.ForeignKey(related_name=b'ages', to='dataentry.Person'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='age',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='district',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='full_name',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='id',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='phone_contact',
        ),
        migrations.RemoveField(
            model_name='interceptee',
            name='vdc',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='id',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_address_district',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_address_vdc',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_age',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_gender',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_name',
        ),
        migrations.RemoveField(
            model_name='victiminterview',
            name='victim_phone',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='address_district',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='address_vdc',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='age',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='id',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='name',
        ),
        migrations.RemoveField(
            model_name='victiminterviewpersonbox',
            name='phone',
        ),
        migrations.AddField(
            model_name='interceptee',
            name='person_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default='', serialize=False, to='dataentry.Person'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='victiminterview',
            name='person_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default='', serialize=False, to='dataentry.Person'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='victiminterviewpersonbox',
            name='person_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default='', serialize=False, to='dataentry.Person'),
            preserve_default=False,
        ),
    ]
