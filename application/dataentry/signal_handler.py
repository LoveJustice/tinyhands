import signal
import sys

from google_sheets import GoogleSheetClientThread


def shutdown_google_sheet_thread(*args):
    GoogleSheetClientThread.shutdown()
    sys.exit()

signal.signal(signal.SIGINT, shutdown_google_sheet_thread)