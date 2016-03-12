import signal
import sys

from google_sheets import google_sheet_client


def shutdown_google_sheet_thread(*args):
    print "in shutdown_google_sheet_thread()"
    google_sheet_client.shutdown()
    sys.exit()
    
signal.signal(signal.SIGINT, shutdown_google_sheet_thread)