from django.apps import AppConfig

from notifications import send_interception_alert_notification


def on_irf_done(sender, **kwargs):
    send_interception_alert_notification()


class FirebaseConfig(AppConfig):
    name = 'firebase'
    verbose_name = 'Firebase'

    def ready(self):
        #add signal listener here
        #signal.connect(on_irf_done, weak=False, dispatch_uid=
        pass
