from django.core.management.base import BaseCommand

from export_import.google_sheet_audit import audit_exports

from dataentry.models import BorderStation, Country
from export_import.mdf_io import export_mdf_sheet
from budget.models import MonthlyDistributionForm

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('country', nargs='+', type=str)
        parser.add_argument('year_month', nargs='+', type=int)
        
        
    def handle(self, *args, **options):
        country_name = options['country'][0]
        year_month = options['year_month'][0]
        year = int(year_month / 100)
        month = year_month % 100
        
        country = Country.objects.get(name=country_name)
        
        print ('Attempting PBS export for country ' + country.name + ' for year ' + str(year) + ' and month ' + str(month))
        
        open_mdf_projects = BorderStation.objects.filter(
                operating_country=country,
                open=True,
                features__contains='hasMDF')
        approved_mdfs = MonthlyDistributionForm.objects.filter(
                status = 'Approved',
                border_station__in=open_mdf_projects,
                month_year__year = year,
                month_year__month = month)
        if len(approved_mdfs) < len(open_mdf_projects):
            # Not all of the MDFs for the country have been approved
            print ('Unable to export open count = ', len(open_mdf_projects), 'approved count =', len(approved_mdfs))
            return False
        
        print('Number of open PBS(' + str(len(open_mdf_projects)) +') matches number of approved PBS(' + str(len(approved_mdfs)) + ').  Starting export' )
        
        export_mdf_sheet(country, year_month)
        
        print('Export complete!')
        
        