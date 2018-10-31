import json
import sys

fixture = ''
for line in sys.stdin:
    fixture += line

db_objs = json.loads(fixture)

sep = '\n'

sys.stdout.write ('[')
for db_obj in db_objs:
    sys.stdout.write(sep)
    sys.stdout.write(json.dumps(db_obj))
    sep = ',\n'
sys.stdout.write('\n]\n')
