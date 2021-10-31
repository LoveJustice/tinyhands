import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.apps import apps

from id_matching.db_conn import DB_Conn
import id_matching.update_matches as um
import id_matching.predict_matches as pm
import id_matching.pre_proc as pp


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--oldLimit',
            action='append',
            type=str,
            help='Specify maximum number of old person records to match',
        )
        
    def handle(self, *args, **options):
        first = datetime.datetime.now()
        persons_to_match = pp.get_and_pre_process_all2(None)
        classifier = pm.load_classifier('/data/id_matching/lr_all.pkl')
        stats = {
            "existing_match":0,
            "new_match":0
        }
        
        if options['oldLimit']:
            process_old_count = int(options['oldLimit'][0])
        else:
            process_old_count = 0
        count = 0
        start = datetime.datetime.now()
        print('setup', start - first)
        msg = "New/updated persons to be matched"
        
        db_conn = DB_Conn(None)
        for outer in range(0,2):
            person_ids = db_conn.ex_query("SELECT id FROM public.dataentry_person where last_match_time is null or last_match_time < last_modified_time;")
            
            print(msg, len(person_ids))
            
            for idx in range(0, len(person_ids)):
                um.update_matches(person_ids.iloc[idx]['id'], persons_to_match, classifier, stats)
                count += 1
                if count % 1000 == 0:
                    current = datetime.datetime.now()
                    diff = current - start
                    print (count, 'records processed in', diff, 'match counts', stats)
            
            if process_old_count > len(person_ids):
                old_update = process_old_count - len(person_ids)
                msg = "Prior persons to be matched"
                db_conn.cur.execute("update dataentry_person set last_match_time = null where id in "\
                            "(select id from dataentry_person where last_match_time > '2100-01-01' limit " + str(old_update) + ")")
                process_old_count = 0
            else:
                break
        
        current = datetime.datetime.now()
        diff = current - start
        print ('completed id match for', count, 'records in', diff, 'match counts', stats)