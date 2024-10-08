# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-01-30 14:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('url', models.CharField(max_length=255, verbose_name='Url')),
                ('tags', models.TextField(blank=True, verbose_name='Tags')),
            ],
        ),
    ]
