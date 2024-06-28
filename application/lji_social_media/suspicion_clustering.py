import pandas as pd
import numpy as np
import json
from llama_index.core import Document
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core import PromptHelper
from libraries.neo4j_lib import execute_neo4j_query
from llama_index.core import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from fb_advert_pages.google_store import write_sheet

# Comparison function
import json
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
import time
from tqdm import tqdm  # Import tqdm for the progress bar

from llama_index.embeddings.openai import OpenAIEmbedding

time.sleep(1)
parameters = {}
query = """MATCH (posting1:Posting)-[reason:IS_MORE_SUSPICIOUS]->(posting2:Posting) RETURN reason.reason AS reason"""
reasons = execute_neo4j_query(query, parameters)

embeddings = []
count = 0
for reason in tqdm(reasons, desc="Processing embeddings"):
    time.sleep(1.1)
    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    embedding = embed_model.get_text_embedding(reason["reason"])
    embeddings.append(embedding)
data = pd.DataFrame(reasons)

data["embeddings"] = embeddings
matrix = np.vstack(data.embeddings.values)
data.to_csv("results/suspicion_reasons.csv", index=False)

from sklearn.cluster import KMeans

n_clusters = 5

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
reasons_list = []
for i in range(n_clusters):
    print(f"Cluster {i} Theme:", end=" ")

    reviews = "\n".join(
        data.loc[data.Cluster == i, "reason"]
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
        model="gpt-4-0125-preview",
        messages=messages,
        temperature=0,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    print(response.choices[0].message.content.replace("\n", ""))
    response.choices[0].message.content.replace("\n", "")
    reasons_list.append(response.choices[0].message.content.replace("\n", ""))
    sample_cluster_rows = data[data.Cluster == i].sample(
        rev_per_cluster, random_state=42
    )
    for j in range(rev_per_cluster):
        # print(sample_cluster_rows.IDn.values[j], end=":   ")
        print(sample_cluster_rows.reason.str[:72].values[j])

    print("-" * 100)
