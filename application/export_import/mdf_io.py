from django.conf import settings

from .google_sheet import GoogleSheet
from dataentry.models import Country
from budget.models import MonthlyDistributionForm, MdfItem
from budget.pdfexports.mdf_exports import MDFExporter
import budget.mdf_constants as constants

def get_mdf_export_rows(keys):
    parts = keys[0].split('-')
    
    category = {}
    for item in constants.CATEGORY_CHOICES:
        category[item[0]] = item[1]
    
    country  = Country.objects.get(id=parts[1])
    mdfs = MonthlyDistributionForm.objects.filter(
            status = 'Approved',
            border_station__operating_country = country,
            month_year__year = parts[0][0:4],
            month_year__month = parts[0][4:])
    
    headers = ['Key','Country','Year Month','MDF Project','Project','Line Item','Amount','Category','Description','Approved By']
    rows = [headers]
    
    for mdf in mdfs:
        mdf_export = MDFExporter(mdf)
        mdf_data = mdf_export.get_mdf_data(mdf)
        for mdf_helper in mdf_data['mdfs']:
            for section in mdf_helper.sections:
                rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code, section.title, section.total,'','',''])
            mdf_items = MdfItem.objects.filter(mdf=mdf)
            for mdf_item in mdf_items:
                if mdf_helper.project.id == mdf_item.work_project.id:
                    if mdf_item.associated_section is None:
                        category_name = 'None'
                    else:
                        category_name = category[mdf_item.associated_section]
                    if mdf_item.category == constants.MONEY_NOT_SPENT:
                        if mdf_item.deduct == 'Yes':
                            rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code,
                                          'Money Not Spent (To Deduct)', mdf_item.cost, category_name, mdf_item.description, mdf_item.approved_by])
                        else:
                            rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code,
                                         'Money Not Spent (Not Deduct)', mdf_item.cost, category_name, mdf_item.description, mdf_item.approved_by])         
                    elif mdf_item.category == constants.PAST_MONTH_SENT:
                        rows.append([keys[0], country.name, parts[0], mdf.border_station.station_code, mdf_helper.project.station_code,
                                     'Past Month Sent Money', mdf_item.cost, category_name, mdf_item.description, mdf_item.approved_by])
    
    return rows

def export_mdf_sheet(country, year_month):
    spreadsheet = 'MDF' + settings.SPREADSHEET_SUFFIX
    sheet = GoogleSheet(spreadsheet,'mdf', 'Key', get_mdf_export_rows)
    
    key = str(year_month) + '-' + str(country.id)
    sheet.update(key, key)

