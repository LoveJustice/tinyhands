from oauth2client.client import GoogleCredentials
from gdata.gauth import OAuth2TokenFromCredentials
from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.spreadsheets.client import ListQuery
from gdata.spreadsheets.data import ListEntry
from multiprocessing import Queue
from threading import Thread

import re
import traceback
import smtplib
import string
import logging
import csv_io
import time

from models import (InterceptionRecord, VictimInterview)
from dataentry_signals import irf_done

from django.conf import settings

logger = logging.getLogger(__name__);

class GoogleSheetClientThread (Thread):

    scope=( "https://www.googleapis.com/auth/drive",
            "https://spreadsheets.google.com/feeds",
            "https://docs.google.com/feeds"
        )

    work_queue = None

    queue_enabled = None
    token = None
    client = None
    spreadsheet_key = None
    import_spreadsheet_key = None
    instance = None
    



    def get_token(self):
        try:
            credentials =  GoogleCredentials.get_application_default()
            credentials = credentials.create_scoped(self.scope)
            self.token = OAuth2TokenFromCredentials(credentials)
            self.have_credentials = True
        except:
            self.have_credentials = False
            logger.warn("No credentials file for google spreadsheet.  No update to google spreadsheets will be attempted.")

    def get_client(self):
        self.client = SpreadsheetsClient()
        self.client = self.token.authorize(self.client)

    def find_spreadsheet_by_name(self, name):
        spreadsheets = self.client.get_spreadsheets()
        for spreadsheet in spreadsheets.entry:
            if (name == spreadsheet.title.text):
                
                return spreadsheet.id.text.rsplit('/',1)[1]

        logger.error("Spreadsheet with the name " + name + " not found")
        return None

    def find_worksheet_by_name(self, spreadsheet_key, name):
        if spreadsheet_key is not None:
            worksheets = self.client.get_worksheets(spreadsheet_key);
            for worksheet in worksheets.entry:
                if (name == worksheet.title.text):
                    return worksheet.id.text.rsplit('/',1)[1]

        logger.error("Worksheet with the name " + name + " not found")
        return None

    @staticmethod
    def spreadsheet_header_from_export_header(hdr):
        hdr = hdr.lower()
        hdr = re.sub("[^a-z0-9\.\-]*","", hdr)
        hdr = re.sub("^[0-9\.\-]*","", hdr)
        return hdr

    def reinitialize(self):
        self.token = None
        self.get_token()
        if self.token is not None:
            self.get_client()
            self.spreadsheet_key = self.find_spreadsheet_by_name(settings.SPREADSHEET_NAME)
            self.irf_worksheet_key = self.find_worksheet_by_name(self.spreadsheet_key, settings.IRF_WORKSHEET_NAME)
            self.vif_worksheet_key = self.find_worksheet_by_name(self.spreadsheet_key, settings.VIF_WORKSHEET_NAME)
            
            self.import_spreadsheet_key = self.find_spreadsheet_by_name(settings.IMPORT_SPREADSHEET_NAME)
            self.irf_import_worksheet_key = self.find_worksheet_by_name(self.import_spreadsheet_key, settings.IRF_IMPORT_WORKSHEET_NAME)
        else:
            logger.error("Unable to get token")

    def __init__(self):
        self.import_status_name = self.spreadsheet_header_from_export_header("Import Status")
        self.import_issues_name = self.spreadsheet_header_from_export_header("Import Issues")
        Thread.__init__(self)
        self.reinitialize()
        if self.have_credentials:
            self.work_queue = Queue()
            self.daemon = True
            self.start()

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
                    logger.error("GoogleSheetClientThread.run Failed to process " + work[0] + " " + work[1] + " on attempt " + str(work[2]) + " - retrying")
                    self.work_queue.put(work);
                else:
                    logger.error("GoogleSheetClientThread.run Failed to process " + work[0] + " " + work[1] + " on attempt " + str(work[2]) + " - giving up\n" + traceback.format_exc())
                    self.send_exception_mail(traceback.format_exc())

    def build_list_entry(self, header_row, data_row):
        list_entry = ListEntry()
        for col_idx in range(0, len(data_row)):
            col_header = self.spreadsheet_header_from_export_header(header_row[col_idx])
            list_entry.set_value(col_header, str(data_row[col_idx]))

        return list_entry


    def update_sheet (self, worksheet_key, key_value, new_rows):
        key_name = self.spreadsheet_header_from_export_header(new_rows[0][0])

        feed = self.client.get_list_feed(self.spreadsheet_key, worksheet_key, query=ListQuery(sq=key_name + "==\"" + key_value + "\""))
        for idx in range(len(feed.entry)-1, -1, -1):
            self.client.delete(feed.entry[idx])

        for row_idx in range(1, len(new_rows)):
            list_entry = self.build_list_entry(new_rows[0], new_rows[row_idx])
            self.client.add_list_entry(list_entry, self.spreadsheet_key, worksheet_key)


    @staticmethod
    def handle_irf_done_signal(sender, **kwargs):
        irf_number = kwargs.get("irf_number")
        GoogleSheetClientThread.update_irf(irf_number)
    
    @staticmethod
    def update_irf(the_irf_number):
        logger.debug("Entry IRF = " + the_irf_number)
        if GoogleSheetClientThread.instance is None:
            GoogleSheetClientThread.instance = GoogleSheetClientThread()

        if GoogleSheetClientThread.instance.have_credentials:
            work = ['IRF', the_irf_number, 0]
            GoogleSheetClientThread.instance.work_queue.put(work)
            logger.debug("IRF added to work queue " + the_irf_number)

    @staticmethod
    def update_vif(the_vif_number):
        logger.debug("Entry VIF = " + the_vif_number)
        if GoogleSheetClientThread.instance is None:
            GoogleSheetClientThread.instance = GoogleSheetClientThread()

        if GoogleSheetClientThread.instance.have_credentials:
            work = ['VIF', the_vif_number, 0]
            GoogleSheetClientThread.instance.work_queue.put(work)
            logger.debug("VIF added to work queue " + the_vif_number)

    def internal_update_irf(self, the_irf_number):
        #print "in internal_update_irf " + the_irf_number
        try:
            irf = InterceptionRecord.objects.get(irf_number = the_irf_number)
            irfs = [irf]
        except:
            logger.info("Could not find IRF " + the_irf_number)
            irfs = []
        new_rows = csv_io.get_irf_export_rows(irfs)
        self.update_sheet(self.irf_worksheet_key, the_irf_number, new_rows)

    def internal_update_vif(self, the_vif_number):
        #print "in internal_update_vif " + the_vif_number
        try:
            vif = VictimInterview.objects.get(vif_number = the_vif_number)
            vifs = [vif]
        except:
            logger.info("Could not find VIF " + the_vif_number)
            vifs = []
        new_rows = csv_io.get_vif_export_rows(vifs)
        self.update_sheet(self.vif_worksheet_key, the_vif_number, new_rows)
    
    @staticmethod
    def import_irfs():
        logger.debug("Entry");
        if GoogleSheetClientThread.instance is None:
            GoogleSheetClientThread.instance = GoogleSheetClientThread()

        if GoogleSheetClientThread.instance.have_credentials:
            logger.info("Starting import from Google Sheet")
            GoogleSheetClientThread.instance.internal_import_irf()
            logger.info("Waiting for export to complete")
            GoogleSheetClientThread.shutdown()
            while not GoogleSheetClientThread.instance.work_queue.empty():
                time.sleep (5)
            logger.info("Finished import from Google Sheet")
        
    def internal_import_irf(self):
        feed = self.client.get_list_feed(self.import_spreadsheet_key, self.irf_import_worksheet_key, query=ListQuery(sq=self.import_status_name + "== Ready"))
        logger.debug("Number of entries to import =" + str(len(feed.entry)))
        for idx in range(len(feed.entry)):
            irfData = feed.entry[idx].to_dict()
        
            errList = csv_io.import_irf_row(irfData)
            if len(errList) > 0:
                if errList[0] == 'IRF already exists':
                    feed.entry[idx].set_value(self.import_status_name, "Existing")
                    feed.entry[idx].set_value(self.import_issues_name, errList[0])
                else:
                    logger.debug("Rejected " + irfData['irfnumber'])
                    feed.entry[idx].set_value(self.import_status_name, "Rejected")
                    sep = ""
                    err_string = ""
                    for err in errList:
                        err_string = err_string + sep + err
                        sep = '\n'
                        
                    feed.entry[idx].set_value(self.import_issues_name, err_string)
                    
            else:
                feed.entry[idx].set_value(self.import_status_name, "Imported")
                feed.entry[idx].set_value(self.import_issues_name, "")
                
            self.client.update(feed.entry[idx])
            
    @staticmethod
    def audit_export_forms():
        logger.debug("Entry");
        if GoogleSheetClientThread.instance is None:
            GoogleSheetClientThread.instance = GoogleSheetClientThread()

        if GoogleSheetClientThread.instance.have_credentials:
            logger.info("Starting audit of exported forms")
            GoogleSheetClientThread.instance.internal_audit_export_sheets()
            logger.info("Finished audit of exported forms")
     
    def get_exported_form_numbers(self, spreadsheet_key, worksheet_key, column_name):
        form_numbers = set()
        feed = self.client.get_list_feed(spreadsheet_key, worksheet_key)
        for idx in range(len(feed.entry)):
            form_data = feed.entry[idx].to_dict()
            form_number = form_data[column_name]
            form_numbers.add(form_number)
        
        return form_numbers
            
    def internal_audit_export_sheets(self):
        form_numbers = self.get_exported_form_numbers(self.spreadsheet_key, self.irf_worksheet_key,
                self.spreadsheet_header_from_export_header('IRF Number'))
        
        irfList = InterceptionRecord.objects.all()
        for irf in irfList:
            if irf.irf_number not in form_numbers:
                logger.debug("IRF Number " + irf.irf_number + " exporting")
                irfs = [irf]
                new_rows = csv_io.get_irf_export_rows(irfs)
                self.update_sheet(self.irf_worksheet_key, irf.irf_number, new_rows)
            else:
                logger.debug("IRF Number " + irf.irf_number + " already exported")
                
        form_numbers = self.get_exported_form_numbers(self.spreadsheet_key, self.vif_worksheet_key,
                self.spreadsheet_header_from_export_header('VIF Number'))
        
        vifList = VictimInterview.objects.all()
        for vif in vifList:
            if vif.vif_number not in form_numbers:
                logger.debug("VIF Number " + vif.vif_number + " exporting")
                vifs = [vif]
                new_rows = csv_io.get_vif_export_rows(vifs)
                self.update_sheet(self.vif_worksheet_key, vif.vif_number, new_rows)
            else:
                logger.debug("VIF Number " + vif.vif_number + " already exported")
                

    def send_exception_mail(self, exception_text):
        try:
            to = []
            for idx in range(0,len(settings.ADMINS)):
                to.append(settings.ADMINS[idx][1])

            if len(to) < 1:
                # There are no admins defined
                return

            frm = settings.DEFAULT_FROM_EMAIL
            body = string.join((
                    "From: %s" % frm,
                    "To: %s" % ", ".join(to),
                    "Subject: %s" % "Exception sending updates to Google Sheets",
                    "",
                    exception_text
                    ), "\r\n")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(frm, to, body)
            server.quit()
        except:
            traceback.print_exc()

    @staticmethod
    def shutdown():
        if GoogleSheetClientThread.instance is not None:
            if GoogleSheetClientThread.instance.have_credentials:
                work = ['SHUTDOWN', '', 0]
                GoogleSheetClientThread.instance.work_queue.put(work)
            
irf_done.connect(GoogleSheetClientThread.handle_irf_done_signal, weak=False, dispatch_uid="GoogleSheetClientThread")
