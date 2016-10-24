from django.conf import settings

from export_import.google_sheet_basic import GoogleSheetBasic
from google_sheet import GoogleSheet
from irf_io import get_irf_export_rows
from vif_io import get_vif_export_rows
from address2_io import get_address2_export_rows

from dataentry.models.interception_record import InterceptionRecord
from dataentry.models.victim_interview import VictimInterview
from dataentry.models.addresses import Address2

def audit_exports():
    audit_irf()
    audit_vif()
    replace_address2()
      
def audit_irf():
    irf_gs = GoogleSheet(settings.SPREADSHEET_NAME, settings.IRF_IMPORT_WORKSHEET_NAME, 'irf Number', get_irf_export_rows)
    
    db_irfs = InterceptionRecord.objects.all()
    irf_gs.audit(db_irfs, 'irf_number')

def audit_vif():
    vif_gs = GoogleSheet(settings.SPREADSHEET_NAME, settings.VIF_IMPORT_WORKSHEET_NAME, 'vif Number', get_vif_export_rows)
    
    db_vifs = VictimInterview.objects.all()
    vif_gs.audit(db_vifs, 'vif_number')
    
def replace_address2():
    addr2 = GoogleSheetBasic(settings.SPREADSHEET_NAME, settings.ADDRESS2_WORKSHEET_NAME)
    
    db_addr2 = Address2.objects.all()
    new_rows = get_address2_export_rows(db_addr2)
    
    reqs = []
    reqs.append(addr2.delete_request(2, addr2.rowCount))
    reqs.append(addr2.expand_request(len(new_rows)))
    reqs.append(addr2.delete_request(1,1))
    addr2.batch_update(reqs)
    
    addr2.append_rows(new_rows)
    
            