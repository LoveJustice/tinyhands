from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0017_monthlydistributionform_money_not_spent_reviewed_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE budget_monthlydistributionmultipliers SET name='Stationery' WHERE name='Stationary'"
        ),
        migrations.RunSQL(
            "UPDATE budget_projectrequest SET benefit_type_name='Stationery' WHERE benefit_type_name='Stationary'"
        ),
        migrations.RunSQL(
            "UPDATE budget_projectrequest SET description='Stationery Total' WHERE description='Stationary Total'"
        ),
    ]
