#!/usr/bin/env python

import argparse
import re
import sqlite3

end_query = re.compile(r'-- END-QUERY (?P<name>[\w-]+)')

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
                    name = match.group('name')
                    result[name] = "\n".join(query_lines)
                    in_query = False
                else:
                    query_lines.append(line)
            else:
                if line.startswith('-- START-QUERY'):
                    query_lines = [ ]
                    in_query = True
    return result

def run_query(db_file_name, query, max_rows=10):
    connection = sqlite3.connect(db_file_name)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query)
    for row in cursor.fetchmany(max_rows):
        print row


parser = argparse.ArgumentParser()
parser.add_argument('--old-query-file', help="Old query file")
parser.add_argument('--new-query-file', help="New query file")
parser.add_argument('--old-db-file', help="Old schema database file", action="append")
parser.add_argument('--new-db-file', help="New schema database file", action="append")
parser.add_argument('--query-name', help="Name of query")
args = parser.parse_args()

old_queries = load_queries(args.old_query_file)
new_queries = load_queries(args.new_query_file)

for file in args.old_db_file:
    print "OLD", file
    run_query(file, old_queries[args.query_name])

for file in args.new_db_file:
    print "NEW", file
    run_query(file, new_queries[args.query_name])
