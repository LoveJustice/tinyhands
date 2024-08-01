import pandas as pd
import streamlit as st
import requests
from libraries.google_lib import DB_Conn
from time import sleep as wait
import os
import streamlit as st
from googlesearch import search
from datetime import datetime, timedelta
import pandas as pd
import tldextract
from libraries.neo4j_lib import Neo4jConnection

curl = st.secrets["face_matcher"]["curl"]


query = """SELECT irfcommon.date_of_interception AS date_of_interception \
        ,irfcommon.irf_number AS irf_number \
        ,person.social_media AS social_media \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.phone_contact AS phone_contact \
        ,person.address_notes AS adress_notes \
        ,person.guardian_name AS guardian_name \
        ,person.guardian_phone AS guardian_phone \
        ,person.address AS address \
        ,irfatt.description AS attachment_description \
        ,irfatt."option" AS attachment_option \
        ,irfatt.attachment AS attachment \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id \
        INNER JOIN public.dataentry_irfattachmentcommon irfatt ON irfatt.interception_record_id = irfcommon.id \
        """

with DB_Conn() as db:
    person_details = db.ex_query(query)
person_details.sort_values("date_of_interception", inplace=True, ascending=False)

person_details.address[0]

filtered_df = person_details[person_details["full_name"].str.split().str.len() > 2]
filtered_df.full_name
deduped_person_details = person_details[~person_details.duplicated(subset="irf_number")]
deduped_person_details = deduped_person_details[
    ~deduped_person_details.duplicated(subset="full_name")
]
deduped_person_details = person_details[~person_details.duplicated(subset="full_name")]
filtered_df = deduped_person_details[
    deduped_person_details["full_name"].str.split().str.len() >= 2
]
filtered_df = filtered_df[~(filtered_df["adress_notes"] == "")]

# Group by irf_number
person_details["date_of_interception"] = pd.to_datetime(
    person_details["date_of_interception"]
)

# Group by irf_number and sort by date_of_interception
grouped = (
    person_details.groupby("irf_number")
    .apply(lambda x: x.sort_values(by="date_of_interception"))
    .reset_index(drop=True)
)

# Aggregate full_name into a unique list, count the number of unique full_name entries, and get the first date_of_interception
result = (
    grouped.groupby("irf_number")
    .agg(
        full_names=("full_name", lambda x: list(pd.Series(x).unique())),
        number_of_names=("full_name", lambda x: len(pd.Series(x).unique())),
        date_of_interception=("date_of_interception", "min"),
        country=("country", "min"),
    )
    .reset_index()
)

# Sort by date_of_interception and then by number_of_names
result = result.sort_values(
    by=["date_of_interception", "number_of_names"], ascending=False
).reset_index(drop=True)

result.loc[3]["full_names"]
# Display the result
print(result)


def get_new_articles(query):
    new_articles = []
    for j in search(
        query,
        # tld="co.in",
    ):
        print(j)
        new_articles.append(j)
    return new_articles


filtered_df["full_name"]


list(filtered_df)
for idx, row in filtered_df[:1].iterrows():
    query = f"{row['full_name']} for human trafficking, country {row['country']}, address {row['adress_notes']}"
    print(idx, query)
    articles = get_new_articles(query)

import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_new_articles(query, api_key, cx):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cx,
    }
    response = requests.get(base_url, params=params)
    results = response.json()

    new_articles = []
    if "items" in results:
        for item in results["items"]:
            new_articles.append(item["link"])

    return new_articles


# You'll need to set up these variables:
api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
cx = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

for idx, row in filtered_df[:2].iterrows():
    query = f"{row['full_name']} for human trafficking, country {row['country']}, address {row['adress_notes']}"
    print(idx, query)
    articles = get_new_articles(query, api_key, cx)

from urllib.parse import urlparse
import requests
from textblob import TextBlob
import datetime


def assess_quality(url, query_terms):
    score = 0
    parsed_url = urlparse(url)
    result = {}
    # Domain authority (simplified example)
    domain = parsed_url.netloc
    if domain.endswith(".edu") or domain.endswith(".gov"):
        score += 10
        result["domain"] = score

    # Keyword matching
    response = requests.get(url)
    content = response.text.lower()
    result["keyword"] = 0
    for term in query_terms:
        if term.lower() in content:
            score += 5
            result["keyword"] += 5

    # Sentiment analysis
    blob = TextBlob(content)
    if blob.sentiment.polarity > 0:
        score += 5
        result["sentiment"] = 5

    # Content freshness
    if "date" in response.headers:
        pub_date = datetime.datetime.strptime(
            response.headers["date"], "%a, %d %b %Y %H:%M:%S GMT"
        )
        if (datetime.datetime.now() - pub_date).days < 30:
            score += 5
            result["freshness"] = 5

    result["total"] = score

    return result


# Usage
url = "https://example.com/article"
query_terms = [row["full_name"], row["country"], row["adress_notes"]]
results = {}
for url in articles:
    print(url)
    quality_score = assess_quality(url, query_terms)
    results[url] = quality_score
    print(f"Quality score: {quality_score}")
