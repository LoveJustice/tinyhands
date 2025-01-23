from libraries.work_with_db import URLDatabase, DatabaseError
db=URLDatabase()
db.create_database()

db.search_urls()