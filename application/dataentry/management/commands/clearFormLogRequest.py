import datetime
import pytz
from django.core.management.base import BaseCommand

from dataentry.models import FormLog

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            action='append',
            type=int,
            help='Number of days that the form log request should be kept',
        )
    
        
    def handle(self, *args, **options):
        if options.get('days'):
            days = options.get('days')[0]
        else:
            days = 30
        
        the_date = datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=days)
        print('Clearing request field prior to ', the_date)
        count = 0
        log_entries = FormLog.objects.filter(date_time__lt=the_date, request__isnull=False)
        for log_entry in log_entries:
            log_entry.request = None
            log_entry.save()
            count += 1
        
        print('Rows Cleared:', count)
        
        
        