# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-10-23 13:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dataentry', '0115_auto_20190919_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='IntercepteeZimbabwe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, default='', upload_to='interceptee_photos')),
                ('anonymized_photo', models.CharField(max_length=126, null=True)),
                ('kind', models.CharField(choices=[('v', 'Victim'), ('t', 'Trafficker'), ('u', 'Unknown')], max_length=4)),
                ('relation_to', models.CharField(blank=True, max_length=255)),
                ('trafficker_taken_into_custody', models.BooleanField(default=False, verbose_name='taken_into_custody')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IrfAttachmentZimbabwe',
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
        migrations.CreateModel(
            name='IrfZimbabwe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='pending', max_length=20, verbose_name='Status')),
                ('date_time_entered_into_system', models.DateTimeField(auto_now_add=True)),
                ('date_time_last_updated', models.DateTimeField(auto_now=True)),
                ('irf_number', models.CharField(max_length=20, unique=True, verbose_name='IRF #:')),
                ('number_of_victims', models.PositiveIntegerField(blank=True, null=True, verbose_name='# of victims:')),
                ('location', models.CharField(max_length=255, verbose_name='Location:')),
                ('date_time_of_interception', models.DateTimeField(verbose_name='Date/Time:')),
                ('number_of_traffickers', models.PositiveIntegerField(blank=True, null=True, verbose_name='# of traffickers')),
                ('staff_name', models.CharField(max_length=255, verbose_name='Staff Name:')),
                ('drugged_or_drowsy', models.BooleanField(default=False, verbose_name='Girl appears drugged or drowsy')),
                ('who_in_group_husbandwife', models.BooleanField(default=False, verbose_name='Husband / Wife')),
                ('married_in_past_2_weeks', models.BooleanField(default=False, verbose_name='Married in the past 2 weeks')),
                ('married_in_past_2_8_weeks', models.BooleanField(default=False, verbose_name='Married within the past 2-8 weeks')),
                ('caught_in_lie', models.BooleanField(default=False, verbose_name='Caught in a lie or contradiction')),
                ('other_red_flag', models.CharField(blank=True, max_length=255)),
                ('where_going_destination', models.CharField(blank=True, max_length=126, verbose_name='Location:')),
                ('where_going_job', models.BooleanField(default=False, verbose_name='Job')),
                ('passport_with_broker', models.BooleanField(default=False, verbose_name='Passport is with a broker')),
                ('job_too_good_to_be_true', models.BooleanField(default=False, verbose_name='Job is too good to be true')),
                ('not_real_job', models.BooleanField(default=False, verbose_name='Not a real job')),
                ('couldnt_confirm_job', models.BooleanField(default=False, verbose_name='Could not confirm job')),
                ('where_going_study', models.BooleanField(default=False, verbose_name='Study')),
                ('no_enrollment_docs', models.BooleanField(default=False, verbose_name='No documentation of enrollment')),
                ('doesnt_know_school_name', models.BooleanField(default=False, verbose_name="Does not Know School's Name and location")),
                ('no_school_phone', models.BooleanField(default=False, verbose_name='No phone number for School')),
                ('not_enrolled_in_school', models.BooleanField(default=False, verbose_name='Not enrolled in school')),
                ('where_runaway', models.BooleanField(default=False, verbose_name='Runaway')),
                ('running_away_over_18', models.BooleanField(default=False, verbose_name='Running away from home (18 years or older)')),
                ('running_away_under_18', models.BooleanField(default=False, verbose_name='Running away from home (under 18 years old)')),
                ('reluctant_family_info', models.BooleanField(default=False, verbose_name='Reluctant to give family info')),
                ('refuses_family_info', models.BooleanField(default=False, verbose_name='Will not give family info')),
                ('under_18_cant_contact_family', models.BooleanField(default=False, verbose_name='No family contact established')),
                ('under_18_family_doesnt_know', models.BooleanField(default=False, verbose_name="Family doesn't know she is going to India")),
                ('under_18_family_unwilling', models.BooleanField(default=False, verbose_name='Family unwilling to let her go')),
                ('talked_to_family_member', models.CharField(blank=True, max_length=127)),
                ('reported_total_red_flags', models.IntegerField(blank=True, null=True, verbose_name='Reported Total Red Flag Points:')),
                ('computed_total_red_flags', models.IntegerField(blank=True, null=True, verbose_name='Computed Total Red Flag Points:')),
                ('who_noticed', models.CharField(max_length=127, null=True)),
                ('staff_who_noticed', models.CharField(blank=True, max_length=255, verbose_name='Staff who noticed:')),
                ('type_of_intercept', models.CharField(max_length=127, null=True)),
                ('how_sure_was_trafficking', models.IntegerField(choices=[(1, '1 - Not at all sure'), (2, '2 - Unsure but suspects it'), (3, '3 - Somewhat sure'), (4, '4 - Very sure'), (5, '5 - Absolutely sure')], null=True, verbose_name='How sure are you that it was trafficking case?')),
                ('convinced_by_staff', models.CharField(blank=True, max_length=127)),
                ('convinced_by_family', models.CharField(blank=True, max_length=127)),
                ('convinced_by_police', models.CharField(blank=True, max_length=127)),
                ('evidence_categorization', models.CharField(max_length=127, null=True)),
                ('reason_for_intercept', models.TextField(blank=True, verbose_name='Primary reason for intercept')),
                ('has_signature', models.BooleanField(default=False, verbose_name='Scanned form has signature?')),
                ('logbook_received', models.DateField(null=True)),
                ('logbook_incomplete_questions', models.CharField(blank=True, max_length=127)),
                ('logbook_incomplete_sections', models.CharField(blank=True, max_length=127)),
                ('logbook_information_complete', models.DateField(null=True)),
                ('logbook_notes', models.TextField(blank=True, verbose_name='Logbook Notes')),
                ('logbook_submitted', models.DateField(null=True)),
                ('logbook_first_verification', models.CharField(blank=True, max_length=127)),
                ('logbook_first_reason', models.TextField(blank=True, verbose_name='First Reason')),
                ('logbook_followup_call', models.CharField(blank=True, max_length=127)),
                ('logbook_first_verification_date', models.DateField(null=True)),
                ('logbook_leadership_review', models.CharField(blank=True, max_length=127)),
                ('logbook_second_verification', models.CharField(blank=True, max_length=127)),
                ('logbook_second_reason', models.TextField(blank=True, verbose_name='Second Reason')),
                ('logbook_second_verification_date', models.DateField(null=True)),
                ('logbook_back_corrected', models.TextField(blank=True, verbose_name='Back Corrected')),
                ('who_in_group_alone', models.BooleanField(default=False, verbose_name='Alone')),
                ('who_in_group_relative', models.BooleanField(default=False, verbose_name='Own brother, sister / relative')),
                ('meeting_someone_across_border', models.BooleanField(default=False, verbose_name='Is meeting a someone just across border')),
                ('traveling_with_someone_not_with_them', models.BooleanField(default=False, verbose_name='Was travelling with someone not with them')),
                ('group_facebook', models.BooleanField(default=False, verbose_name='Facebook')),
                ('group_other_website', models.CharField(blank=True, max_length=127)),
                ('relationship_social_media', models.BooleanField(default=False, verbose_name='Met on social media')),
                ('relationship_to_get_married', models.BooleanField(default=False, verbose_name='Coming to get married')),
                ('with_non_relative', models.BooleanField(default=False, verbose_name='With non-relatives')),
                ('met_within_past_2_months', models.BooleanField(default=False, verbose_name='Met within the past 2 months')),
                ('dont_know_or_conflicting_answers', models.BooleanField(default=False, verbose_name='They don’t know or provide conflicting answers')),
                ('undocumented_children_in_group', models.BooleanField(default=False, verbose_name='Undocumented child(ren) in the group')),
                ('met_on_the_way', models.BooleanField(default=False, verbose_name='Met on their way')),
                ('group_young_women_kids', models.BooleanField(default=False, verbose_name='Group of young women / kids')),
                ('who_in_group_engaged', models.BooleanField(default=False, verbose_name='Engaged')),
                ('who_in_group_dating', models.BooleanField(default=False, verbose_name='Dating couple')),
                ('who_in_group_pv_under_14', models.BooleanField(default=False, verbose_name='PV is under 14')),
                ('relationship_arranged_by_other', models.BooleanField(default=False, verbose_name='Non-relative(s) organized their travel')),
                ('host_non_relative_paid', models.BooleanField(default=False, verbose_name='Non-relative(s) paid their travel expenses')),
                ('mobile_phone_taken_away', models.BooleanField(default=False, verbose_name='Their mobile phone was taken away')),
                ('contradiction_between_stories', models.BooleanField(default=False, verbose_name='Contradiction between stories')),
                ('wife_under_18', models.BooleanField(default=False, verbose_name='Wife/fiancee is under 18')),
                ('employment_massage_parlor', models.BooleanField(default=False, verbose_name='Massage parlor')),
                ('employment_salon', models.BooleanField(default=False, verbose_name='Salon')),
                ('young_woman_going_to_mining_town', models.BooleanField(default=False, verbose_name='Young woman going for a job in a mining town')),
                ('person_speaking_on_their_behalf', models.BooleanField(default=False, verbose_name='Person is not speaking on their own behalf / someone is speaking for them')),
                ('seasonal_farm_work', models.BooleanField(default=False, verbose_name='Going for seasonal farm work')),
                ('unregistered_mine', models.BooleanField(default=False, verbose_name='Going to work at unregistered mine')),
                ('no_company_website', models.BooleanField(default=False, verbose_name='Could not find company website')),
                ('distant_relative_paying_for_education', models.BooleanField(default=False, verbose_name='Distant relative is paying for education')),
                ('no_school_website', models.BooleanField(default=False, verbose_name='No school website')),
                ('doesnt_speak_destination_language', models.BooleanField(default=False, verbose_name="Doesn't speak language of destination")),
                ('where_going_doesnt_know', models.BooleanField(default=False, verbose_name="Don't know where they are going")),
                ('job_confirmed', models.BooleanField(default=False, verbose_name='Job confirmed')),
                ('valid_id_or_enrollment_documents', models.BooleanField(default=False, verbose_name='Valid ID card or enrollment documents')),
                ('enrollment_confirmed', models.BooleanField(default=False, verbose_name='Enrollment confirmed')),
                ('purpose_for_going_other', models.CharField(blank=True, max_length=127)),
                ('which_contact', models.CharField(blank=True, max_length=127)),
                ('name_of_contact', models.CharField(blank=True, default='', max_length=127)),
                ('initial_signs', models.CharField(blank=True, default='', max_length=127)),
                ('case_notes', models.TextField(blank=True, verbose_name='Case Notes')),
                ('form_entered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='irfzimbabwe_entered_by', to=settings.AUTH_USER_MODEL)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataentry.BorderStation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='irfattachmentzimbabwe',
            name='interception_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataentry.IrfZimbabwe'),
        ),
        migrations.AddField(
            model_name='intercepteezimbabwe',
            name='interception_record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interceptees', to='dataentry.IrfZimbabwe'),
        ),
        migrations.AddField(
            model_name='intercepteezimbabwe',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dataentry.Person'),
        ),
    ]
