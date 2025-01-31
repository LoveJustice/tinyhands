import sqlite3
import os
import pandas as pd

db_path = os.getenv("HTDB_PATH")

with sqlite3.connect(db_path) as conn:
    cursor = conn.execute("SELECT * FROM urls")
    urls = cursor.fetchall()
    pd.DataFrame(urls, columns=[description[0] for description in cursor.description]).to_csv('output/urls.csv',
                                                                                              index=False)
    cursor = conn.execute("SELECT * FROM suspects")
    suspects = cursor.fetchall()
    pd.DataFrame(suspects, columns=[description[0] for description in cursor.description]).to_csv('output/suspects.csv',
                                                                                                  index=False)

    cursor = conn.execute("SELECT * FROM incidents")
    incidents = cursor.fetchall()
    pd.DataFrame(incidents, columns=[description[0] for description in cursor.description]).to_csv(
        'output/incidents.csv', index=False)

    cursor = conn.execute("SELECT * FROM suspect_forms")
    suspect_forms = cursor.fetchall()
    pd.DataFrame(suspect_forms, columns=[description[0] for description in cursor.description]).to_csv(
        'output/suspect_forms.csv', index=False)

    cursor = conn.execute("SELECT * FROM victims")
    suspect_forms = cursor.fetchall()
    pd.DataFrame(suspect_forms, columns=[description[0] for description in cursor.description]).to_csv(
        'output/victims.csv', index=False)

    cursor = conn.execute("SELECT * FROM victim_forms")
    suspect_forms = cursor.fetchall()
    pd.DataFrame(suspect_forms, columns=[description[0] for description in cursor.description]).to_csv(
        'output/victim_forms.csv', index=False)








