from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0003_district_vdc'),
    ]

    operations = [
        # Removed AddField in 0002, so no need to remove.
        # migrations.RemoveField(
        #     model_name='victiminterviewlocationbox',
        #     name='geolocation',
        # ),
        migrations.DeleteModel(
            name='GeoCodeLocation',
        ),
        migrations.AddField(
            model_name='vdc',
            name='cannonical_name',
            field=models.ForeignKey(blank=True, to='dataentry.VDC', null=True),
            preserve_default=True,
        ),
        # To be removed in 0006, so don't add.
        # migrations.AddField(
        #     model_name='victiminterviewlocationbox',
        #     name='district_geocodelocation',
        #     field=models.ForeignKey(default=None, to='dataentry.District'),
        #     preserve_default=False,
        # ),
        # migrations.AddField(
        #     model_name='victiminterviewlocationbox',
        #     name='vdc_geocodelocation',
        #     field=models.ForeignKey(default=None, to='dataentry.VDC'),
        #     preserve_default=False,
        # ),
        migrations.AlterField(
            model_name='vdc',
            name='district',
            field=models.ForeignKey(to='dataentry.District'),
        ),
    ]
