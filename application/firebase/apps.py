from django.apps import AppConfig

from dataentry.dataentry_signals import irf_done
from notifications import send_interception_alert_notification


def on_irf_done(sender, **kwargs):
    send_interception_alert_notification()


class FirebaseConfig(AppConfig):
    name = 'firebase'
    verbose_name = 'Firebase'

    def ready(self):
        irf_done.connect(on_irf_done, weak=False, dispatch_uid="IRFFirebaseNotification")
