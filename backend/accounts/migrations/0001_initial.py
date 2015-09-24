# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=255)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('permission_irf_view', models.BooleanField(default=False)),
                ('permission_irf_add', models.BooleanField(default=False)),
                ('permission_irf_edit', models.BooleanField(default=False)),
                ('permission_irf_delete', models.BooleanField(default=False)),
                ('permission_vif_view', models.BooleanField(default=False)),
                ('permission_vif_add', models.BooleanField(default=False)),
                ('permission_vif_edit', models.BooleanField(default=False)),
                ('permission_vif_delete', models.BooleanField(default=False)),
                ('permission_accounts_manage', models.BooleanField(default=False)),
                ('permission_receive_email', models.BooleanField(default=False)),
                ('permission_border_stations_view', models.BooleanField(default=False)),
                ('permission_border_stations_add', models.BooleanField(default=False)),
                ('permission_border_stations_edit', models.BooleanField(default=False)),
                ('permission_vdc_manage', models.BooleanField(default=False)),
                ('permission_budget_manage', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('activation_key', models.CharField(default=accounts.models.make_activation_key, max_length=40)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'account',
                'verbose_name_plural': 'accounts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('email_template', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'alert',
                'verbose_name_plural': 'alerts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultPermissionsSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('permission_irf_view', models.BooleanField(default=False)),
                ('permission_irf_add', models.BooleanField(default=False)),
                ('permission_irf_edit', models.BooleanField(default=False)),
                ('permission_irf_delete', models.BooleanField(default=False)),
                ('permission_vif_view', models.BooleanField(default=False)),
                ('permission_vif_add', models.BooleanField(default=False)),
                ('permission_vif_edit', models.BooleanField(default=False)),
                ('permission_vif_delete', models.BooleanField(default=False)),
                ('permission_accounts_manage', models.BooleanField(default=False)),
                ('permission_receive_email', models.BooleanField(default=False)),
                ('permission_border_stations_view', models.BooleanField(default=False)),
                ('permission_border_stations_add', models.BooleanField(default=False)),
                ('permission_border_stations_edit', models.BooleanField(default=False)),
                ('permission_vdc_manage', models.BooleanField(default=False)),
                ('permission_budget_manage', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='alert',
            name='permissions_group',
            field=models.ManyToManyField(to='accounts.DefaultPermissionsSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='user_designation',
            field=models.ForeignKey(related_name='accounts', to='accounts.DefaultPermissionsSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
