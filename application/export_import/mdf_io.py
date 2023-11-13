from django.conf import settings

from .google_sheet import GoogleSheet
from dataentry.models import Country
from budget.models import MonthlyDistributionForm
from budget.pdfexports.mdf_exports import MDFExporter

def get_mdf_export_rows(keys):
    parts = keys[0].split('-')
    
    country  = Country.objects.get(id=parts[1])
    mdfs = MonthlyDistributionForm.objects.filter(
            status = 'Approved',
            border_station__operating_country = country,
            month_year__year = parts[0][0:4],
            month_year__month = parts[0][4:])
    
    headers = ['Key','Country','Year Month','MDF Project','Project','Line Item','Amount']
    rows = [headers]
    
    for mdf in mdfs:
        mdf_export = MDFExporter(mdf)
        mdf_data = mdf_export.get_mdf_data(mdf)
        for mdf_helper in mdf_data['mdfs']:
            for section in mdf_helper.sections:
                rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code, section.title, section.total])
            rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code, 'Past Month Sent Money', mdf_helper.past_money_sent_total])
            rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code, 'Money Not Spent (To Deduct)', mdf_helper.money_not_spent_total])
            rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code, 'Money Not Spent (Not Deduct)',
                         mdf.money_not_spent_not_deduct_total(mdf_helper.project)])
    
    return rows

def export_mdf_sheet(country, year_month):
    spreadsheet = 'MDF' + settings.SPREADSHEET_SUFFIX
    sheet = GoogleSheet(spreadsheet,'mdf', 'Key', get_mdf_export_rows)
    
    key = str(year_month) + '-' + str(country.id)
    sheet.update(key, key)

