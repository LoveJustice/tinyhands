# imports
import numpy as np
import pandas as pd
from ast import literal_eval
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(model="text-embedding-3-large")


from libraries.neo4j_lib import execute_neo4j_query

parameters = {}
query = """MATCH (n:Posting) WHERE (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.text AS advert"""
postings = execute_neo4j_query(query, parameters)
pd.DataFrame(postings).to_csv("results/adverts.csv", index=False)
adverts = pd.read_csv("results/adverts.csv")
adverts["advert"][1]

query = """MATCH (g:Group)-[:HAS_POSTING]-(n:Posting) WHERE (g.country_id) = 1 AND (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.text AS advert"""
postings = execute_neo4j_query(query, parameters)
pd.DataFrame(postings).sample(100).to_csv("results/adverts_za_sample.csv", index=False)

embeddings = []
for posting in postings:
    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    embedding = embed_model.get_text_embedding(posting["advert"])
    embeddings.append(embedding)
data = pd.DataFrame(postings)
data["embeddings"] = embeddings
matrix = np.vstack(data.embeddings.values)

from sklearn.cluster import KMeans

n_clusters = 7

kmeans = KMeans(n_clusters=n_clusters, init="k-means++", random_state=42)
kmeans.fit(matrix)
labels = kmeans.labels_
data["Cluster"] = labels

from sklearn.manifold import TSNE
import matplotlib
import matplotlib.pyplot as plt

tsne = TSNE(
    n_components=2, perplexity=15, random_state=42, init="random", learning_rate=200
)
vis_dims2 = tsne.fit_transform(matrix)

x = [x for x, y in vis_dims2]
y = [y for x, y in vis_dims2]

for category, color in enumerate(["purple", "green", "red", "blue"]):
    xs = np.array(x)[data.Cluster == category]
    ys = np.array(y)[data.Cluster == category]
    plt.scatter(xs, ys, color=color, alpha=0.3)

    avg_x = xs.mean()
    avg_y = ys.mean()

    plt.scatter(avg_x, avg_y, marker="x", color=color, s=100)
plt.title("Clusters identified visualized in language 2d using t-SNE")

from openai import OpenAI
import os

client = OpenAI()

# Reading a review which belong to each group.
rev_per_cluster = 5

for i in range(n_clusters):
    print(f"Cluster {i} Theme:", end=" ")

    reviews = "\n".join(
        data[data.Cluster == i]
        # .combined.str.replace("Title: ", "")
        # .str.replace("\n\nContent: ", ":  ")
        .sample(rev_per_cluster, random_state=42)
        .apply(lambda x: str(x))
        .values
    )

    messages = [
        {
            "role": "user",
            "content": f'What do the following adverts have in common?\n\nAdverts:\n"""\n{reviews}\n"""\n\nTheme:',
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response.choices[0].message.content.replace("\n", ""))

    sample_cluster_rows = data[data.Cluster == i].sample(
        rev_per_cluster, random_state=42
    )
    for j in range(rev_per_cluster):
        print(sample_cluster_rows.IDn.values[j], end=":   ")
        print(sample_cluster_rows.Text.str[:70].values[j])

    print("-" * 100)
