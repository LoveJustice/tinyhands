import os
from pathlib import Path
from dotenv import load_dotenv
from work_with_db import URLDatabase  # Replace with the actual module name where URLDatabase is defined

# Load environment variables (ensure HTDB_PATH is set)
load_dotenv()

# List of URLs you want to delete from the database.
delete_urls = ['https://www.herald.co.zw/human-trafficker-convicted-sentencing-on-tomorrow/',
'https://www.herald.co.zw/human-trafficker-convicted-sentencing-on-tomorrow/',
'https://www.thestar.com/news/world/asia/china-detains-suspect-in-human-trafficking-cases-linked-to-online-scam-networks-in-myanmar/article_6f9bc2f1-695c-5f57-882c-5914586c491e.html',
'https://www.belgrade-news.com/news/briefs/senior-israeli-member-of-orthodox-jewish-sect-lev-tahor-arrested-for-alleged-human-trafficking/article_29fe7f90-dd0d-11ef-95e9-7f26ee63097a.html',
'https://www.hindustantimes.com/india-news/three-more-held-in-inter-state-child-trafficking-racket-belagavi-sp-101738004232680.html',
'https://obamawhitehouse.archives.gov/blog/2012/11/26/fighting-human-trafficking-cambodia',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://www.destinyrescue.org/our-work/where-we-work/cambodia/',
'https://crownschool.uchicago.edu/student-life/advocates-forum/sex-trafficking-cambodia-complex-humanitarian-emergency',
               'https://www.yahoo.com/news/joint-operation-targeting-online-child-185108812.html']

def delete_urls_from_db(db: URLDatabase, urls: list) -> None:
    """
    Delete the given list of URLs from the database.
    Because the foreign keys in related tables (victims, suspects, etc.)
    are defined with ON DELETE CASCADE, deleting rows from the 'urls'
    table will automatically remove all dependent records.
    """
    if not urls:
        db.logger.info("No URLs provided for deletion.")
        return

    # Create a string of placeholders for the parameterized query.
    placeholders = ",".join("?" for _ in urls)
    query = f"DELETE FROM urls WHERE url IN ({placeholders})"

    # Execute the query within the context manager that handles connections and errors.
    with db._execute_query(query, tuple(urls)) as cursor:
        if cursor.rowcount > 0:
            db.logger.info(f"Deleted {cursor.rowcount} URL(s) from the database.")
        else:
            db.logger.warning("No matching URLs found to delete.")

if __name__ == "__main__":
    # Initialize the database handler.
    db = URLDatabase()  # Ensure that HTDB_PATH is set in your environment

    # Delete the specified URLs.
    delete_urls_from_db(db, delete_urls)
