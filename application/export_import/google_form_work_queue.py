from threading import Thread
from multiprocessing import Queue

import logging
import traceback
from export_import.google_sheet import GoogleSheet
from dataentry.dataentry_signals import form_done
from .form_io import get_form_export_rows
from .export_form import ExportFormFactory
from dataentry.models import FormType

logger = logging.getLogger(__name__);

class GoogleFormWorkQueue(Thread):
    instance = None
    have_credentials = False
    sheet_dict = {}
    
    def __init__(self):
        sheet_cache = {}
        try:
            Thread.__init__(self)
            self.work_queue = Queue()
            self.daemon = True
            self.start()
        except:
            logger.warn("Exception thrown " + traceback.format_exc())
    
    def reinitialize(self):
        self.sheet_dict = {}

    def run(self):
        while True:
            work = self.work_queue.get()
            logger.info("in run " + str(work[0]))
            try:
                self.internal_update(work[0], work[1])
            except:
                logger.error("Failed to process " + str(work[0]) + " on attempt " + str(work[2]))
                self.reinitialize();
                work[2] = work[2] + 1
                if work[2] < 2:
                    logger.error("GoogleFormWorkQueue.run Failed to process " + str(work[0]) + " on attempt " + str(work[1]) + " - retrying")
                    self.work_queue.put(work);
                else:
                    logger.error("GoogleFormWorkQueue.run Failed to process " + str(work[0]) + " on attempt " + str(work[1]) + " - giving up\n" + traceback.format_exc())
                    self.send_exception_mail(traceback.format_exc())
                    break
    
    def find_sheet(self, obj, station, form_type):
        export_forms = ExportFormFactory.find_by_instance(obj)
        if len(export_forms) < 1:
            sheet = None
        else:
            config = export_forms[0].google_sheet_config
            if config is None:
                sheet =  None
            else:
                sheet = GoogleSheet.from_form_config(config)
                
        if station not in self.sheet_dict:
            self.sheet_dict[station] = {}
            
        self.sheet_dict[station][form_type] = sheet
        
        return sheet
    
    def internal_update(self, obj, remove):
        station = obj.station
        form_type = obj.get_form_type_name()
        if station in self.sheet_dict and form_type in self.sheet_dict[station]:
            sheet = self.sheet_dict[station][form_type]
        else:
            sheet = self.find_sheet(obj, station, form_type)
            
        if sheet is not None:
            if remove == True:
                obj = None
            sheet.update(obj.get_key(), obj)
        
    @staticmethod
    def update_form(form_data, remove):
        try:
            logger.debug("form_data=" + str(form_data))
            if GoogleFormWorkQueue.instance is None:
                GoogleFormWorkQueue.instance = GoogleFormWorkQueue()          
                logger.debug("Back from creating GoogleFormWorkQueue")
    
            work = [form_data, remove, 0]
            GoogleFormWorkQueue.instance.work_queue.put(work)
            logger.debug("added to work queue form data=" + str(form_data))
        except:
            logger.warn("Exception thrown " + traceback.format_exc())
        
    @staticmethod
    def handle_form_done_signal(sender, **kwargs):
        form_data = kwargs.get("form_data")
        remove = kwargs.get("remove")
        if remove is None:
            remove = False

        GoogleFormWorkQueue.update_form(form_data.form_object, remove)
        
        
form_done.connect(GoogleFormWorkQueue.handle_form_done_signal, weak=False, dispatch_uid="GoogleFormWorkQueue")
