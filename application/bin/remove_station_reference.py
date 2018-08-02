# Export of the dataentry_form table will contain foreign keys to entries
# in the dataentry_borderstation table.  These represent the contents of the
# dataentry_form_stations table.  Since ID values may not have the same values
# in the target system, these the foreign keys removed.
import json
import sys

if len(sys.argv) != 3:
    print ("must provide input and output file names")
    sys.exit()

str = open(sys.argv[1], 'r').read()
db_objs = json.loads(str)

for db_obj in db_objs:
    if db_obj['model'] == 'dataentry.form':
        db_obj['fields']['stations'] = []


out_str = json.dumps(db_objs)

with open(sys.argv[2], "w") as out_file:
    out_file.write(out_str)
