import pandas as pd
import streamlit as st
import requests
from libraries.google_lib import DB_Conn
from time import sleep as wait

curl = st.secrets["face_matcher"]["curl"]


def save_attachment(response, filename):
    if response.status_code == 200:
        # Define the path where you want to save the file
        att_file_path = f"attachments/{filename}"
        # Write the content to a file
        with open(att_file_path, "wb") as att_file:
            att_file.write(response.content)
        print("File saved successfully.")
    else:
        print("Failed to retrieve the file.")


query = """SELECT irfcommon.date_of_interception AS date_of_interception \
        ,person.social_media AS social_media \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.adress_notes AS adress_notes \
        ,irfatt.description AS attachment_description \
        ,irfatt."option" AS attachment_option \
        ,irfatt.attachment AS attachment \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id
        INNER JOIN public.dataentry_irfattachmentcommon irfatt ON irfatt.interception_record_id = irfcommon.id"""

with DB_Conn() as db:
    social_media = db.ex_query(query)
social_media.sort_values("date_of_interception", inplace=True, ascending=False)

list(social_media)
# Slice the DataFrame
filtered_social_media = social_media[
    social_media["attachment_description"].str.contains(
        "conversation", case=False, na=False
    )
]

# Display the result
print(filtered_social_media)


filtered_social_media.date_of_interception = pd.to_datetime(
    filtered_social_media.date_of_interception
)

audio_curl = curl["url"] + "scanned_irf_forms/KMB144_KMB144_voice%20note.ogg"
response = requests.get(audio_curl, auth=(curl["email"], curl["password"]))
for attachment in filtered_social_media[:100].attachment:
    wait(5)
    print(attachment)
    att_curl = curl["url"] + attachment
    response = requests.get(att_curl, auth=(curl["email"], curl["password"]))
    save_attachment(response, attachment.split("/")[-1])


social_media_column = social_media[~social_media["social_media"].isna()].sort_values(
    "date_of_interception"
)


social_media.sort_values("date_of_interception")["social_media"].tolist()
social_media.sort_values("date_of_interception")[["social_media"]].tolist()
social_media[
    [
        "irf_number",
        "role",
        "social_media",
        "attachment_description",
        "attachment_option",
        "attachment",
    ]
]
social_media[["irf_number", "role", "social_media"]].tolist()
social_media.role.unique()
social_media
query = """select irf.irf_number, att.description, att."option", att.attachment, irf.date_of_interception, c.name as country
from dataentry_irfcommon irf join dataentry_borderstation bs on bs.id = irf.station_id join dataentry_country c on c.id = bs.operating_country_id join dataentry_irfattachmentcommon att on att.interception_record_id = irf.id
where  att."option" is null"""

with DB_Conn() as db:
    attachments = db.ex_query(query)

list(attachments)
attachments[attachments.country == "Nepal"]
attachments.attachment.tolist()
attachments.loc[attachments["irf_number"] == "LWK764"]
curl = st.secrets["face_matcher"]["curl"]
attachment_name = "APP1290_APP1290 FACEBOOK.jpg"
att_curl = curl["url"] + f"scanned_irf_forms/{attachment_name}"
response = requests.get(att_curl, auth=(curl["email"], curl["password"]))
save_attachment(response, attachment_name)

from time import sleep as wait

attachments.date_of_interception = pd.to_datetime(attachments.date_of_interception)
audio_curl = curl["url"] + "scanned_irf_forms/KMB144_KMB144_voice%20note.ogg"
response = requests.get(audio_curl, auth=(curl["email"], curl["password"]))
for attachment in attachments[:100].attachment:
    wait(5)
    print(attachment)
    att_curl = curl["url"] + attachment
    response = requests.get(att_curl, auth=(curl["email"], curl["password"]))
    save_attachment(response, attachment.split("/")[-1])
