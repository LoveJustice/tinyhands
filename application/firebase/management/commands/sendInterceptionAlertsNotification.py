from django.core.management.base import BaseCommand
from django.utils import timezone

from dataentry.models.interception_alert import InterceptionAlert
from firebase.notifications import send_interception_alert_notification


class Command(BaseCommand):
    help = 'Sends firebase notification telling number of new interception alerts in the past 24 hours'

    def handle(self, *args, **options):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)
        self.stdout.write('One day ago is ' + str(one_day_ago))
        new_alert_count = InterceptionAlert.objects.filter(created__gt=one_day_ago).count()
        self.stdout.write('New alerts found: ' + str(new_alert_count))
        if new_alert_count > 0:
            message = self.create_message(new_alert_count)
            self.stdout.write('Sending message: ' + message)
            send_interception_alert_notification(message)
            self.stdout.write('Message sent')
        else:
            self.stdout.write('Send no notifications')

    @staticmethod
    def create_message(alert_count):
        message = str(alert_count) + ' new victims intercepted in the past 24 hours'
        return message
