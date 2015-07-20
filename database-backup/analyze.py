#!/usr/bin/env python

import re
import sqlite3
import sys

end_query = re.compile(r'-- END-QUERY (?P<age>[\w-]+) (?P<name>[\w-]+)')

def load_queries(file_name):
    """Load queries from text file."""
    result = { }
    in_query = False
    query_lines = None
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if in_query:
                match = re.match(end_query, line)
                if match:
                    age = match.group('age')
                    if age not in result:
                        result[age] = { }
                    name = match.group('name')
                    result[age][name] = "\n".join(query_lines)
                    in_query = False
                else:
                    query_lines.append(line)
            else:
                if line.startswith('-- START-QUERY'):
                    query_lines = [ ]
                    in_query = True
    return result

query = { }
for arg in sys.argv[1:3]:
    result = load_queries(arg)
    query.update(result)

db_file_name = sys.argv[3]                # TODO
q = query['new']['interceptee']

print query, db_file_name

connection = sqlite3.connect(db_file_name)
cursor = connection.cursor()
cursor.execute(q)
print cursor.fetchone()
