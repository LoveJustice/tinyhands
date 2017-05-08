from threading import Thread
from multiprocessing import Queue

import logging
import traceback
from dataentry.models.interception_record import InterceptionRecord
from export_import.google_sheet import GoogleSheet
from django.conf import settings
from irf_io import get_irf_export_rows
from vif_io import get_vif_export_rows
from dataentry.models.victim_interview import VictimInterview
from dataentry.dataentry_signals import irf_done, vif_done


logger = logging.getLogger(__name__);

class GoogleSheetWorkQueue(Thread):
    instance = None
    have_credentials = False
    
    def __init__(self):
        try:
            logger.debug("In __init__") 
            self.irf_sheet = GoogleSheet.from_settings('IRF')
            logger.debug("Returned for allocating IRF have_credentails=" + str(self.irf_sheet.credentials)) 
            self.vif_sheet = GoogleSheet.from_settings('VIF')
            logger.debug("Returned from allocating VIF have_credentails=" + str(self.vif_sheet.credentials)) 
            if self.irf_sheet.credentials and self.vif_sheet.credentials:
                logger.debug("have credentials")
                Thread.__init__(self)
                self.have_credentials = True
                self.work_queue = Queue()
                self.daemon = True
                self.start()
            else:
                logger.warn("Missing credentials")
        except:
            logger.warn("Exception thrown " + traceback.format_exc())
    
    def reinitialize(self):
        self.irf_sheet.get_sheet_metadata()
        self.vif_sheet.get_sheet_metadata()

    def run(self):
        while True:
            work = self.work_queue.get()
            logger.info("in run " + work[0] + ", " + work[1])
            try:
                if work[0] == 'IRF':
                    self.internal_update_irf(work[1])
                elif work[0] == 'VIF':
                    self.internal_update_vif(work[1])
                elif work[0] == "SHUTDOWN":
                    self.work_queue.close()
                    self.have_credentials = False
                    return
                else:
                    logger.error("Unknown work type " + work[0])
            except:
                logger.error("Failed to process " + work[0] + " " + work[1] + " on attempt " + str(work[2]))
                self.reinitialize();
                work[2] = work[2] + 1
                if work[2] < 2:
                    logger.error("GoogleSheetWorkQueue.run Failed to process " + work[0] + " " + work[1] + " on attempt " + str(work[2]) + " - retrying")
                    self.work_queue.put(work);
                else:
                    logger.error("GoogleSheetWorkQueue.run Failed to process " + work[0] + " " + work[1] + " on attempt " + str(work[2]) + " - giving up\n" + traceback.format_exc())
                    self.send_exception_mail(traceback.format_exc())
                    break
    
    def internal_update_irf(self, the_irf_number):
        irf = None
        try:
            irf = InterceptionRecord.objects.get(irf_number = the_irf_number)            
        except:
            logger.info("Could not find IRF " + the_irf_number)
    
        self.irf_sheet.update(the_irf_number, irf)
        

    def internal_update_vif(self, the_vif_number):
        vif = None
        try:
            vif = VictimInterview.objects.get(vif_number = the_vif_number)
        except:
            logger.info("Could not find VIF " + the_vif_number)
        
        self.vif_sheet.update(the_vif_number, vif)
        
    @staticmethod
    def update_form(form_number, form_type):
        try:
            logger.debug("form_number=" + form_number + ", form_type=" + form_type)
            if GoogleSheetWorkQueue.instance is None:
                GoogleSheetWorkQueue.instance = GoogleSheetWorkQueue()
            
            logger.debug("Back from creating GoogleSheetWorkQueue")
    
            if GoogleSheetWorkQueue.instance.have_credentials:
                work = [form_type, form_number, 0]
                GoogleSheetWorkQueue.instance.work_queue.put(work)
                logger.debug("added to work queue form type=" + form_type + "form number=" + form_number)
            else:
                logger.debug("No credentials")
        except:
            logger.warn("Exception thrown " + traceback.format_exc())
        
    @staticmethod
    def handle_irf_done_signal(sender, **kwargs):
        irf_number = kwargs.get("irf_number")
        GoogleSheetWorkQueue.update_form(irf_number, 'IRF')
        
    @staticmethod
    def handle_vif_done_signal(sender, **kwargs):
        vif_number = kwargs.get("vif_number")
        GoogleSheetWorkQueue.update_form(vif_number, 'VIF')
        
irf_done.connect(GoogleSheetWorkQueue.handle_irf_done_signal, weak=False, dispatch_uid="GoogleSheetWorkQueue")
vif_done.connect(GoogleSheetWorkQueue.handle_vif_done_signal, weak=False, dispatch_uid="GoogleSheetWorkQueue")
