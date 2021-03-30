import calendar
import datetime

from dataentry.models import Country, IndicatorHistory
from dataentry.views.indicators import IndicatorsViewSet
def get_data_collection_indicator_export_rows(year_months):
    headers = [
            'year month',
            'year',
            'month',
            'country name',
            'station code',
            'Number of Victims',
            'IRFs',
            'IRFs in Compliance Number',
            'IRFs in Compliance Percent',
            'IRF Collection Lag Time',
            'CIFs',
            'CIF Percent',
            'CIF in Compliance Number',
            'CIF in Compliance Percent',
            'CIF Collection Lag Time',
            'Number of CIFs with "Evidence"',
            'VDFs',
            'VDFs in Compliance Number',
            'VDFs in Compliance Percent',
            'VDF Collection Lag Time',
            'Total Number of Verified Forms',
            'Evidence',
            'Evidence Percent',
            'Invalid Intercept',
            'Invalid Intercept Percent',
            'High Risk of Trafficking',
            'High Risk of Trafficking Percent',
            'VDF Percent',
            'V Photos Percent',
            'Compliance Percent',
            'Collection Lag Time',
            'Evidence Cases with CIF Percent',
            'Percent of Valid Intercepts',
            'Percent Phone Numbers Verified',
            'Total'
        ]
    
    year_month = year_months[0]
    
    year = int(year_month[:4])
    month = int (year_month[4:])
    
    start_date = datetime.date(year, month,1)
    end_date = datetime.date(year, month, calendar.monthrange(year,month)[1])
    
    rows = []
    rows.append(headers)
    
    countries = Country.objects.all()
    for country in countries:
        results = IndicatorsViewSet.compute_collection_indicators(start_date, end_date, country.id)
        for result in results:
            row = []
            row.append(year_month)
            row.append(year)
            row.append(month)
            row.append(country.name)
            row.append(result['label'])
            row.append(result['victim_count'])
            
            row.append(result['irf_count'])
            row.append(result['irf_compliance_count'])
            row.append(result['irf_compliance_percent'])
            row.append(result['irf_lag'])

            row.append(result['cif_count'])
            row.append(result['cif_percent'])
            row.append(result['cif_compliance_count'])
            row.append(result['cif_compliance_percent'])
            row.append(result['cif_lag'])
            row.append(result['cif_with_evidence_count'])
            
            row.append(result['vdf_count'])
            row.append(result['vdf_compliance_count'])
            row.append(result['vdf_compliance_percent'])
            row.append(result['vdf_lag'])
            
            row.append(result['verified_forms'])
            row.append(result['evidence_count'])
            row.append(result['evidence_percent'])
            row.append(result['invalid_intercept_count'])
            row.append(result['invalid_intercept_percent'])
            row.append(result['high_risk_count'])
            row.append(result['high_risk_percent'])
            
            row.append(result['vdf_percent'])
            row.append(result['photo_percent'])
            row.append(result['compliance_percent'])
            row.append(result['collection_lag_time'])
            row.append(result['evidence_cif_percent'])
            row.append(result['valid_intercept_percent'])
            row.append(result['phone_verified_percent'])
            row.append(result['compliance_total'])
            
            rows.append(row)
    
    return rows

def get_data_entry_indicator_export_rows(year_months):
    headers = [
        'year month',
        'year',
        'month',
        'country name',
        "IRF Lag Time",
        "IRF Forms Entered",
        "IRF Original Form Attached %",
        "Photo Upload Lag Time",
        "Photos Uploaded",
        "VDF Lag Time",
        "VDF Forms Entered",
        "VDF Original Form Attached %",
        "CIF Lag Time",
        "CIF Forms Entered",
        "CIF Original Form Attached %", 
        "Step 1: Verification Lag time",
        "Step 1: Verifications Completed",
        "Step 1: Verification Backlog",
        "Step 1: Verification Victims",
        "Step 2: Verification Lag time",
        "Step 2: Verifications Completed",
        "Step 2: Verification Backlog",
        "Step 2: Verification Victims"
    ]
    indicators = [
        "irfLag",
        "irfCount",
        "irfOriginalFormPercent",
        "photosLag",
        "photosCount",
        "vdfLag",
        "vdfCount",
        "vdfOriginalFormPercent",
        "cifLag",
        "cifCount",
        "cifOriginalFormPercent",
        "v1Lag",
        "v1Count",
        "v1Backlog",
        "v1VictimCount",
        "v2Lag",
        "v2Count",
        "v2Backlog",
        "v2VictimCount"
        ]
    rows = []
    rows.append(headers)
    
    year_month = year_months[0]

    year = int(year_month[:4])
    month = int (year_month[4:])
    
    start_date = datetime.date(year, month,1)
    end_date = datetime.date(year, month, calendar.monthrange(year,month)[1])
    
    countries = Country.objects.all()
    for country in countries:
        result = IndicatorHistory.calculate_indicators(start_date, end_date, country, include_latest_date=True)
        row = []
        row.append(year_month)
        row.append(year)
        row.append(month)
        row.append(country.name)
        for indicator in indicators:
            if indicator in result and result[indicator] != '-':
                row.append(result[indicator])
            else:
                row.append("")
        rows.append(row)
    
    return rows
            