from threading import Thread
from multiprocessing import Queue
import logging
import traceback
from django.conf import settings

from dataentry.dataentry_signals import form_done, background_form_done


logger = logging.getLogger(__name__);

class WorkElement:
    def __init__(self, form_data, remove):
        self.form_data = form_data
        self.remove = remove
    
    def __str__(self):
        if self.form_data is None:
            return 'No form data'
        else:
            return str(self.form_data)

class WorkTask:
    def __init__(self, name, method):
        self.name  = name
        self.method = method
    
    def __str__(self):
        return self.name

class BackgroundFormWork(Thread):
    instance = None
    
    def __init__(self):
        try:
            Thread.__init__(self)
            self.work_queue = Queue()
            self.daemon = True
            self.start()
        except Exception:
            logger.warn("Exception thrown " + traceback.format_exc())

    def run(self):
        while True:
            work = self.work_queue.get()
            background_form_done.send_robust(sender=self.__class__, form_data=work.form_data, remove=work.remove)
                    
    @staticmethod
    def add_work(sender, **kwargs):
        if settings.TEST_ENVIRONMENT:
            # Test environment, doe not initialize thread or attempt to update google sheet
            return
        
        form_data = kwargs.get("form_data")
        remove = kwargs.get("remove")
        if remove is None:
            remove = False    
        work = WorkElement(form_data, remove)
        
        if BackgroundFormWork.instance is None:
                BackgroundFormWork.instance = BackgroundFormWork()
  
        BackgroundFormWork.instance.work_queue.put(work)
        logger.debug("added to background queue form data=" + work)
                    
form_done.connect(BackgroundFormWork.add_work, weak=False, dispatch_uid="BackgroundFormWork")