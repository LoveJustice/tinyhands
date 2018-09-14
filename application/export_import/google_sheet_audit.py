import logging

from export_import.google_sheet_basic import GoogleSheetBasic
from .google_sheet import GoogleSheet
from .address2_io import get_address2_export_rows
from .export_form import ExportToGoogleSheet

from dataentry.models.interception_record import InterceptionRecord
from dataentry.models.victim_interview import VictimInterview
from dataentry.models.interceptee import Interceptee
from dataentry.models.addresses import Address2

logger = logging.getLogger(__name__);

def audit_exports():
    logger.info("Begin audit")
    ExportToGoogleSheet.audit_forms()
    audit_irf()
    audit_vif()
    audit_traffickers()
    replace_address2()
    logger.info("Complete audit")
      
def audit_irf():
    logger.info("Begin IRF audit")
    irf_gs = GoogleSheet.from_settings('IRF')
    
    db_irfs = InterceptionRecord.objects.all()
    irf_gs.audit(db_irfs, 'irf_number')
    logger.info("Complete IRF audit")

def audit_vif():
    logger.info("Begin IRF audit")
    vif_gs = GoogleSheet.from_settings('VIF')
    
    db_vifs = VictimInterview.objects.all()
    vif_gs.audit(db_vifs, 'vif_number')
    logger.info("Complete IRF audit")

def audit_traffickers():
    logger.info("begin Trafficker audit")
    trafficker_gs = GoogleSheet.from_settings('Traffickers')
    
    db_traffickers = Interceptee.objects.filter(kind='t').exclude(photo__isnull=True)
    trafficker_gs.audit(db_traffickers, 'id')
    logger.info("Complete Trafficker audit")
    
def replace_address2():
    logger.info("Begin replace Address2")
    addr2 = GoogleSheetBasic.from_settings('ADDRESS2')
    
    db_addr2 = Address2.objects.all().order_by('address1__name', 'name')
    new_rows = get_address2_export_rows(db_addr2)
    
    # You cannot remove all of the rows from a worksheet - so
    #   1) remove all but the header row
    #   2) Expand the worksheet to hold all of the new rows
    #   3) remove the old header row
    #   4) append the new rows which includes a header row
    reqs = []
    reqs.append(addr2.delete_request(1, addr2.rowCount))
    reqs.append(addr2.expand_request(len(new_rows)))
    reqs.append(addr2.delete_request(0,0))
    addr2.batch_update(reqs)
    
    addr2.append_rows(new_rows)
    logger.info("Complete replace Address2")


        
    
    
            
