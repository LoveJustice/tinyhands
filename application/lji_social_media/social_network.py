import pandas as pd

from libraries.google_lib import DB_Conn
import streamlit as st

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


query = """SELECT irfcommon.irf_number AS irf_number \
        ,irfcommon.date_of_interception AS date_of_interception \
        ,person.social_media AS social_media \
        ,person.social_media_platform AS social_media_platform \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.address_notes AS address_notes \
        ,country.name AS country \
        ,country.id AS operating_country_id \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_borderstation borderstation ON borderstation.id = irfcommon.station_id \
        INNER JOIN public.dataentry_country country ON country.id = borderstation.operating_country_id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id"""

with DB_Conn() as db:
    social_media = db.ex_query(query)
social_media.sort_values("date_of_interception", inplace=True, ascending=False)
list(social_media)
social_media.to_csv("results/social_media.csv", index=False)
social_media[social_media.social_media_platform == "Facebook"]
query = f"{trafficking_query_part} after:{start_date_str} before:{end_date_str}"
social_media.social_media.unique()


query = """SELECT irfcommon.irf_number AS irf_number \
        ,irfcommon.date_of_interception AS date_of_interception \
        ,person.social_media AS social_media \
        ,person.social_media_platform AS social_media_platform \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.address_notes AS address_notes \
        FROM public.dataentry_irfcommon irfcommon \
        INNER JOIN public.dataentry_intercepteecommon intercepteecommon ON intercepteecommon.interception_record_id = irfcommon.id \
        INNER JOIN public.dataentry_person person ON person.id = intercepteecommon.person_id"""

with DB_Conn() as db:
    social_media = db.ex_query(query)
social_media.sort_values("date_of_interception", inplace=True, ascending=False)

query = """SELECT person.social_media AS social_media \
        ,person.social_media_platform AS social_media_platform \
        ,person.role AS role \
        ,person.full_name AS full_name \
        ,person.nationality AS nationality \
        ,person.address_notes AS address_notes \
        FROM public.dataentry_person person \
"""
with DB_Conn() as db:
    social_media = db.ex_query(query)
# social_media.sort_values("date_of_interception", inplace=True, ascending=False)

social_media.social_media.unique()
social_media.social_media_platform.unique()

facebook_variations = [
    "Facebook",
    "FACEBOOK",
    "facebook",
    "Faceboook",
    "Facebbok",
    "Facebppk",
    "Fcaebook",
    "Dacebook",
    "Facebok",
    "Facbook",
    "Facaebook",
    "Faebook",
    "Fcebook",
    "Facebokk",
    "Facebool",
    "Faccebook",
    "FPakistanACEBOOK",
    "Face  book",
    "Face book",
    "Faceook",
    "Face Book",
    "FaceBook",
    "F acebbok",
    "Facebook`",
    "Facebook and Instagram",
    "Facebook/Instagram",
    "FB & Instagram",
    "FB/Instagram",
]

# Renaming all variations to "Facebook"
social_media["social_media_platform"] = social_media["social_media_platform"].replace(
    facebook_variations, "Facebook"
)

social_media["social_media_platform"].unique()
filter = social_media["social_media_platform"] == "Facebook"
roles = list(social_media["role"].unique())
social_media[filter]


from llama_index.embeddings.openai import OpenAIEmbedding

# Display the cleaned dataframe
print(social_media)

embedding_dict = {}
embeddings = []
for role in roles:
    if role:
        embed_model = OpenAIEmbedding(model="text-embedding-3-large")
        embedding = embed_model.get_text_embedding(role)
        embedding_dict[role] = embedding
        embeddings.append(embedding_dict)
    else:
        pass

# matrix = np.vstack(data.embeddings.values)

pd.DataFrame(embeddings).to_csv("results/role_embeddings.csv", index=False)
from sklearn.metrics import silhouette_score

# Calculate silhouette scores for different numbers of clusters
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Calculate inertia for different numbers of clusters
inertia = []
k_values = range(1, 20)
for k in k_values:
    kmeans = KMeans(n_clusters=k, init="k-means++", random_state=42)
    kmeans.fit(matrix)
    inertia.append(kmeans.inertia_)

# Plot the inertia values to visualize the elbow
plt.figure(figsize=(8, 6))
plt.plot(k_values, inertia, marker="o")
plt.xlabel("Number of Clusters")
plt.ylabel("Inertia")
plt.title("Elbow Method for Optimal Number of Clusters")
plt.show()

silhouette_scores = []
k_values = range(2, 20)
for k in k_values:
    kmeans = KMeans(n_clusters=k, init="k-means++", random_state=42)
    kmeans.fit(matrix)
    labels = kmeans.labels_
    silhouette_scores.append(silhouette_score(matrix, labels))

# Plot the silhouette scores to visualize the best number of clusters
plt.figure(figsize=(8, 6))
plt.plot(k_values, silhouette_scores, marker="o")
plt.xlabel("Number of Clusters")
plt.ylabel("Silhouette Score")
plt.title("Silhouette Scores for Optimal Number of Clusters")
plt.show()


list(social_media)
for index, row in social_media.iterrows():
    query = f"{row['full_name']} from {row['']}"
    if row["role"] in embedding_dict:
        social_media.loc[index, "role_embedding"] = embedding_dict[row["role"]]
    else:
        social_media.loc[index, "role_embedding"] = None

from googlesearch import search

query = f"{row['full_name']} from {row['']}"
new_articles = []
filter = social_media[social_media["full_name"] == ""]
row = social_media[~(social_media["address_notes"] == "")].iloc[1]
query = f"{row['full_name']} from {row['address_notes']}"
for j in search(
    query,
):
    print(j)
    new_articles.append(j)
    sear
