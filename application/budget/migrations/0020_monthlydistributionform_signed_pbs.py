# Generated by Django 4.2.10 on 2024-10-28 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0019_alter_mdfitem_associated_section_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlydistributionform',
            name='signed_pbs',
            field=models.FileField(blank=True, default='', upload_to='pbs_attachments'),
        ),
    ]
