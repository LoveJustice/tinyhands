from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('dataentry', '0057_auto_20180730_1616'),
    ]
    
    operations = [
       migrations.RunSQL("UPDATE dataentry_permission SET account_permission_name = 'permission_vif_delete' where permission_group = 'VIF' and action='DELETE';"),
    ]
