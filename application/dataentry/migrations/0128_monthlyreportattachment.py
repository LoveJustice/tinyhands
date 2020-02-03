# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-01-15 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0128_auto_20200116_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyReportAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_number', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(max_length=126, null=True)),
                ('attachment', models.FileField(upload_to='mrf_attachments', verbose_name='Attach scanned copy of form (pdf or image)')),
                ('private_card', models.BooleanField(default=True)),
                ('option', models.CharField(max_length=126, null=True)),
                ('monthly_report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataentry.MonthlyReport')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]