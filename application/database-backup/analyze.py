#!/usr/bin/env python

import argparse

from util import load_queries, run_query

def process_query(db_file_name, query, max_rows=10):
    cursor = run_query(db_file_name, query)
    for row in cursor.fetchmany(max_rows):
        print row


parser = argparse.ArgumentParser()
parser.add_argument('--old-query-file', help="Old query file")
parser.add_argument('--new-query-file', help="New query file")
parser.add_argument('--old-db-file', help="Old schema database file", action="append")
parser.add_argument('--new-db-file', help="New schema database file", action="append")
parser.add_argument('--query-name', help="Name of query")
args = parser.parse_args()

if args.old_db_file:
    old_queries = load_queries(args.old_query_file)
    for file in args.old_db_file:
        print "OLD", file
        process_query(file, old_queries[args.query_name])

if args.new_db_file:
    new_queries = load_queries(args.new_query_file)
    for file in args.new_db_file:
        print "NEW", file
        process_query(file, new_queries[args.query_name])
