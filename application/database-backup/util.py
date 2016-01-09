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

def run_query(db_file_name, query):
    connection = sqlite3.connect(db_file_name)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor

