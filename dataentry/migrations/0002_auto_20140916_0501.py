from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoCodeLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('place_name', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('level', models.TextField(max_length=5, choices=[(b'S', b'State'), (b'D', b'District'), (b'V', b'VDC'), (b'C', b'City')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        # migrations.AddField(
        #     model_name='victiminterviewlocationbox',
        #     name='geolocation',
        #     field=models.ForeignKey(related_name=b'geolocation', default='', to='dataentry.GeoCodeLocation'),
        #     preserve_default=False,
        # ),
    ]
