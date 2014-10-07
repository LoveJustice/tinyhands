from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dataentry', '0002_auto_20140916_0501'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VDC',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('district', models.ForeignKey(related_name=b'district_name', to='dataentry.District', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
