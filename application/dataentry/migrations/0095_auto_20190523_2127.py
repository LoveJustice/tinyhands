# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-05-23 21:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0094_auto_20190509_1713'),
    ]

    operations = [
        migrations.CreateModel(
            name='IrfAttachmentBenin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_number', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(max_length=126, null=True)),
                ('attachment', models.FileField(upload_to='scanned_irf_forms', verbose_name='Attach scanned copy of form (pdf or image)')),
                ('private_card', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='appears_under_spell',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='doesnt_speak_local_language',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='going_abroad_domestic_work',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='handed_over_to',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='interception_made',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='job_just_graduated',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='non_relative_met_within_past_2_months',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='relationship_social_media',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='scanned_form',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='visa_for_domestic_work',
        ),
        migrations.RemoveField(
            model_name='irfbenin',
            name='where_going_middle_east',
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='contradiction_between_stories',
            field=models.BooleanField(default=False, verbose_name='Contradiction between stories'),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='destination_other',
            field=models.CharField(blank=True, max_length=127),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='evidence_categorization',
            field=models.CharField(max_length=127, null=True),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='purpose_for_going_other',
            field=models.CharField(blank=True, max_length=127),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='reason_for_intercept',
            field=models.TextField(blank=True, verbose_name='Primary reason for intercept'),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='who_in_group_dating',
            field=models.BooleanField(default=False, verbose_name='Dating Couple'),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='who_in_group_engaged',
            field=models.BooleanField(default=False, verbose_name='Engaged'),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='who_in_group_pv_under_14',
            field=models.BooleanField(default=False, verbose_name='PV is under 14'),
        ),
        migrations.AddField(
            model_name='irfbenin',
            name='wife_under_18',
            field=models.BooleanField(default=False, verbose_name='Wife/fiancee is under 18'),
        ),
        migrations.AddField(
            model_name='irfattachmentbenin',
            name='interception_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataentry.IrfBenin'),
        ),
    ]
