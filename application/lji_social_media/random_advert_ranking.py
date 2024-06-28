import pandas as pd
import re
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from libraries.neo4j_lib import execute_neo4j_query
from fb_advert_pages.google_store import write_sheet
import random
import json
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

llm = OpenAI(temperature=0.01, model="gpt-4o")
memory = ChatMemoryBuffer.from_defaults(token_limit=32000)

query = """MATCH (loser:Posting), (winner:Posting) WHERE ID(loser)=$loser_idn AND ID(winner)=$winner_idn WITH loser, winner
MERGE (winner)<-[:IS_MORE_SUSPICIOUS {reason:$reason}]-(loser)"""


def get_adverts():
    query = """MATCH (n:Posting) WHERE (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.post_id, n.post_url AS post_url, n.text AS advert"""
    postings = execute_neo4j_query(query, {})
    return pd.DataFrame(postings)


def calculate_page_rank(graph_name):
    parameters = {"graph_name": graph_name}
    query = """CALL gds.pageRank.stream($graph_name)
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).post_url AS post_url, score, nodeId AS IDn
    ORDER BY score DESC, post_url, nodeId ASC"""
    result = execute_neo4j_query(query, parameters)
    return result


def drop_graph(graph_name):
    parameters = {"graph_name": graph_name}
    query = """CALL gds.graph.drop($graph_name)"""
    result = execute_neo4j_query(query, parameters)
    return result


def create_graph(graph_name):
    parameters = {"graph_name": graph_name}
    query = """CALL gds.graph.project($graph_name, 'Posting', 'IS_MORE_SUSPICIOUS')"""
    result = execute_neo4j_query(query, parameters)
    return result


def graph_stats(graph_name):
    parameters = {"graph_name": graph_name}
    query = """CALL gds.pageRank.stats($graph_name, {
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD centralityDistribution
RETURN centralityDistribution.max AS max"""
    return execute_neo4j_query(query, parameters)


def score_adverts():
    query = """CALL gds.pageRank.stats('myGraph', {
  maxIterations: 20,
  dampingFactor: 0.85
})
YIELD centralityDistribution
RETURN centralityDistribution.max AS max"""


def draw_pairs(df, n):
    """
    Draw n pairs of rows from the DataFrame df with replacement,
    ensuring no pair contains the same row twice.

    :param df: DataFrame from which pairs are to be drawn
    :param n: Number of pairs to draw
    :return: List of tuples, each containing two DataFrame rows
    """
    num_rows = len(df)
    pairs = []

    for _ in range(n):
        idx1 = random.randint(0, num_rows - 1)
        idx2 = random.randint(0, num_rows - 1)
        # Ensure idx2 is different from idx1
        while idx2 == idx1:
            idx2 = random.randint(0, num_rows - 1)

        pair = (df.iloc[idx1], df.iloc[idx2])
        pairs.append(pair)

    return pairs


def compare_adverts(index, prompt, max_retries=7):
    chat_engine = create_chat_engine(index)
    attempt = 0
    while attempt < max_retries:
        response = chat_engine.chat(prompt)
        formatted_response = (
            response.response.strip()
        )  # Remove leading/trailing whitespace

        try:
            return json.loads(formatted_response)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1} failed with JSON Decode Error:", e)
            print(
                "Response received:", formatted_response[:500]
            )  # Print first 500 chars for context

            # Attempt to fix common JSON errors
            fixed_json = try_fix_json(formatted_response)
            if fixed_json:
                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    pass  # If fix doesn't work, continue to retry

            attempt += 1
            if attempt == max_retries:
                print("Maximum retry attempts reached. Returning None.")
                return None
    return None


def get_ids(comparison, IDn_a, IDn_b):
    if comparison["most suspect"] == "advert_a":
        winner_IDn, loser_IDn = IDn_a, IDn_b
    elif comparison["most suspect"] == "advert_b":
        winner_IDn, loser_IDn = IDn_b, IDn_a
    else:
        winner_IDn, loser_IDn = IDn_a, IDn_b
    return winner_IDn, loser_IDn


def try_fix_json(broken_json):
    # Example fix: remove trailing commas before closing brackets or braces
    try:
        fixed_json = re.sub(r",\s*([}\]])", r"\1", broken_json)
        return fixed_json
    except Exception as e:
        print("Failed to fix JSON:", e)
        return None


def create_advert_prompt():
    return """Assistant, please examine the two documents metadata advert {advert_a} and {advert_b}. Both documents are employment advertisements. Your task is to evaluate which advertisement is more likely to be associated with human trafficking by misrepresenting job opportunities for the purpose of exploiting victims. Determine whether one, both, or neither of these advertisements is suspect in this context.
If an advertisement does not seem to be aimed at employment exploitation, specify this clearly and then do not express an opinion on suspicion..
Your analysis should be thorough, with a focus on aspects such as the language used, the nature of the job offered, and any discrepancies or unusual elements in the advertisements.
Be consistent, objective, precise, and detailed in your evaluation.
If there is no evidence of suspicious activity in either advertisement, explicitly state this conclusion.
Do not make up any conclusion.

Please provide your response in the following JSON format and ensure it can be parsed correctly:
{{
  "most suspect": "advert_a" or "advert_b" or "neither",
  "reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."
}}"""


def create_chat_engine(index):
    memory.reset()
    return index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "As a career forensic analyst you have deep insight into crime and criminal activity especially the field of "
            "online human trafficking. "
            "You are careful and precise and can compare adverts in the finest detail."
            "You are specifically looking for perpetrators who are using employment advertisements to exploit victims. "
        ),
    )


from time import sleep
import random

adverts = get_adverts()
idns = adverts["IDn"].to_list()
# Shuffling the list
random.shuffle(idns)

adverta = adverts.loc[adverts.IDn == idns[0], "advert"].values[0]
advertb = adverts.loc[adverts.IDn == idns[1], "advert"].values[0]


pairs = draw_pairs(adverts, 600)
query = """MATCH (loser:Posting), (winner:Posting) WHERE ID(loser)=$loser_node AND ID(winner)=$winner_node WITH loser, winner
MERGE (winner)<-[:IS_MORE_SUSPICIOUS {reason:$reason}]-(loser)"""
for pair in pairs:
    print(pair[0]["IDn"])
    sleep(2)
    node_a, advert_a, node_b, advert_b = (
        str(pair[0]["IDn"]),
        pair[0]["advert"],
        str(pair[1]["IDn"]),
        pair[1]["advert"],
    )
    advert_prompt = create_advert_prompt(node_a, node_b)
    documents = [
        Document(
            text=advert_a,
            metadata={"IDn": node_a, "advert": "advert_a"},
        ),
        Document(
            text=advert_b,
            metadata={"IDn": node_b, "advert": "advert_b"},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)

    if comparison is not None:
        if comparison["most suspect"] != "neither":
            winner_node, loser_node = get_ids(comparison, node_a, node_b)
            parameters = {
                "winner_node": int(winner_node),
                "loser_node": int(loser_node),
                "reason": comparison["reasoning"],
            }
            print(parameters)
            execute_neo4j_query(query, parameters)
        elif comparison["most suspect"] == "neither":
            print("No suspicious activity detected")

if comparison is None:
    print(True)


drop_graph("suspicion_graph")
create_graph("suspicion_graph")
page_rank = calculate_page_rank("suspicion_graph")
graph_stats("suspicion_graph")
scored_adverts = pd.DataFrame(page_rank)[["post_url", "score"]].merge(
    adverts, on="post_url"
)
scored_adverts["score"] = scored_adverts.score * 1000
scored_adverts["score"] = scored_adverts["score"].astype(int)
write_sheet("scored_adverts", scored_adverts)
advert_sample = pd.read_csv("data_sources/advert_sample.csv", encoding="latin1")
advert_sample = advert_sample[~advert_sample.post_url.isnull()][
    [
        "post_id",
        "post_url",
        "advert",
        "Rating 1 - 10 (10 is most likely to be HT)",
        "Reason",
    ]
]
list(scored_adverts)
list(advert_sample.columns)
comparison = scored_adverts.merge(advert_sample, on="post_url")

for idx, row in comparison.iterrows():
    print(row["post_url"])
    query = """MATCH (n:Posting) WHERE n.post_url=$post_url WITH n
    MATCH (n)<-[reason:IS_MORE_SUSPICIOUS]-(other_posting:Posting) RETURN n.post_url AS post_url, reason.reason AS reason, other_posting.post_url AS other_post_url"""
    parameters = {"post_url": row["post_url"]}
    # print(parameters)
    reason = execute_neo4j_query(query, parameters)
    print(reason)

node_a, node_b = 573283, 573604
advert_a, advert_b = (
    adverts.loc[adverts.IDn == node_a, "advert"].values[0],
    adverts.loc[adverts.IDn == node_b, "advert"].values[0],
)
advert_prompt = create_advert_prompt(node_a, node_b)

documents = [
    Document(
        text=advert_a,
        metadata={"IDn": node_a, "advert": "advert_a"},
    ),
    Document(
        text=advert_b,
        metadata={"IDn": node_b, "advert": "advert_b"},
    ),
]
index = VectorStoreIndex.from_documents(documents, llm=llm)
comparison = compare_adverts(index, advert_prompt)


node_a, node_b = 573283, 573366
advert_a, advert_b = (
    adverts.loc[adverts.IDn == node_a, "advert"].values[0],
    adverts.loc[adverts.IDn == node_b, "advert"].values[0],
)
advert_prompt = create_advert_prompt(node_a, node_b)

documents = [
    Document(
        text=advert_a,
        metadata={"IDn": node_a, "advert": "advert_a"},
    ),
    Document(
        text=advert_b,
        metadata={"IDn": node_b, "advert": "advert_b"},
    ),
]
index = VectorStoreIndex.from_documents(documents, llm=llm)
comparison = compare_adverts(index, advert_prompt)


advert_prompt = create_advert_prompt()
advert_urls = advert_sample.post_url.to_list()


results = []
reasons = []
for index_a in range(len(advert_urls) - 1):
    advert_urla = advert_urls[index_a]
    advert_a = advert_sample[advert_sample.post_url == advert_urla]["advert"].values[0]
    print(advert_a)
    for index_b in range(index_a + 1, len(advert_urls)):
        advert_urlb = advert_urls[index_b]
        advert_b = advert_sample[advert_sample.post_url == advert_urlb][
            "advert"
        ].values[0]
        documents = [
            Document(
                text=advert_a,
                metadata={"advert": "advert_a"},
            ),
            Document(
                text=advert_b,
                metadata={"advert": "advert_b"},
            ),
        ]
        index = VectorStoreIndex.from_documents(documents, llm=llm)
        comparison = compare_adverts(index, advert_prompt)
        if comparison is not None:
            if comparison["most suspect"] == "advert_a":
                outcome = (index_a, index_b)
            elif comparison["most suspect"] == "advert_b":
                outcome = (index_b, index_a)
            else:
                outcome = ()
            reason = [advert_a, advert_b, comparison["reasoning"]]
            reasons.append(reason)
            results.append(outcome)


reasons_df = pd.DataFrame(reasons)
reasons_df.columns = ["advert_a", "advert_b", "reasoning"]
combined_results = pd.DataFrame(results)
combined_results.columns = ["more_suspicious", "less_suspicious"]
# combined_results.more_suspicious.astype(int)
combined_results = combined_results.merge(reasons_df, left_index=True, right_index=True)


import networkx as nx


# List of tuples representing directional relationships

edges = [t for t in results if t]
reversed_edges = [(m, n) for n, m in edges]
# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph (relationship is (n)<-[]-(m))
G.add_edges_from(reversed_edges)

# Calculate PageRank
pagerank = nx.pagerank(G)

# Print the PageRank values
print("PageRank values:")
for node, rank in pagerank.items():
    print(f"Node {node}: {rank}")

# Optionally, add the PageRank values to your DataFrame
pagerank_df = pd.DataFrame(list(pagerank.items()), columns=["Node", "PageRank"])
print("\nPageRank DataFrame:")
print(pagerank_df)
pagerank_df_sample = pagerank_df.merge(advert_sample, left_on="Node", right_index=True)
pagerank_df_sample.to_csv("results/pagerank_df_sample_2.csv", index=False)

pagerank_df_sample = pd.read_csv("results/pagerank_df_sample_2.csv")

list(pagerank_df_sample)
df = combined_results.merge(
    pagerank_df_sample, left_on="more_suspicious", right_on="Node"
)
df.rename(
    columns={
        "Reason": "monitor_more_suspicious_reason",
        "Rating 1 - 10 (10 is most likely to be HT)": "monitor_more_suspicious_rating",
        "PageRank": "more_suspicious_pagerank",
    },
    inplace=True,
)
list(df)
df = df.merge(
    pagerank_df_sample[
        ["Node", "Reason", "Rating 1 - 10 (10 is most likely to be HT)", "PageRank"]
    ],
    left_on="less_suspicious",
    right_on="Node",
)
df.rename(
    columns={
        "Reason": "monitor_less_suspicious_reason",
        "Rating 1 - 10 (10 is most likely to be HT)": "monitor_less_suspicious_rating",
        "PageRank": "less_suspicious_pagerank",
    },
    inplace=True,
)


pagerank_df_sample_1 = pd.read_csv("results/pagerank_df_sample.csv")
df.drop(columns=["Node_x", "Node_y"], inplace=True)
df = df.merge(
    pagerank_df_sample_1[["PageRank", "Node"]],
    left_on="more_suspicious",
    right_on="Node",
)
df.rename(columns={"PageRank": "more_suspicious_pagerank_0"}, inplace=True)
df = df.merge(
    pagerank_df_sample_1[["PageRank", "Node"]],
    left_on="less_suspicious",
    right_on="Node",
)
df.rename(columns={"PageRank": "less_suspicious_pagerank_0"}, inplace=True)
df = df.merge(
    pagerank_df_sample_1[["PageRank", "Node"]],
    left_on="less_suspicious",
    right_on="Node",
)

# df.rename(columns={"PageRank": "less_suspicious_pagerank_0"}, inplace=True)
df.drop(columns=["Node_x", "Node_y"], inplace=True)
list(df)

df["more_suspicious_pagerank"] = df["more_suspicious_pagerank"].astype(float) * 1000
df["more_suspicious_pagerank_0"] = df["more_suspicious_pagerank_0"].astype(float) * 1000
df["less_suspicious_pagerank"] = df["less_suspicious_pagerank"].astype(float) * 1000
df["less_suspicious_pagerank_0"] = df["less_suspicious_pagerank_0"].astype(float) * 1000
df["more_suspicious_pagerank"] = df["more_suspicious_pagerank"] * 1000
df["more_suspicious_pagerank_0"] = df["more_suspicious_pagerank_0"] * 1000
df["less_suspicious_pagerank"] = df["less_suspicious_pagerank"] * 1000
df["less_suspicious_pagerank_0"] = df["less_suspicious_pagerank_0"] * 1000
df["more_suspicious_pagerank"] = df["more_suspicious_pagerank"].astype(int)
df["more_suspicious_pagerank_0"] = df["more_suspicious_pagerank_0"].astype(int)
df["less_suspicious_pagerank"] = df["less_suspicious_pagerank"].astype(int)
df["less_suspicious_pagerank_0"] = df["less_suspicious_pagerank_0"].astype(int)
df["more_suspicious"] = df["more_suspicious"].astype(int)
df["less_suspicious"] = df["less_suspicious"].astype(int)
list(df)
columns = [
    "advert",
    "advert_a",
    "advert_b",
    "more_suspicious",
    "less_suspicious",
    "monitor_more_suspicious_rating",
    "monitor_less_suspicious_rating",
    "more_suspicious_pagerank",
    "less_suspicious_pagerank",
    "more_suspicious_pagerank_0",
    "less_suspicious_pagerank_0",
    "monitor_more_suspicious_reason",
    "monitor_less_suspicious_reason",
    "reasoning",
    "post_id",
    "post_url",
]
df[columns].to_csv("results/combined_results.csv", index=False)
df.sort_values("more_suspicious", ascending=False, inplace=True)

node_list = df["more_suspicious"].unique()
results = []
for node in node_list:
    print(node)
    text = df[df["more_suspicious"] == node]["reasoning"].str.cat(sep=" ")
    memory.reset()

    documents = [
        Document(text=text),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "As a career forensic analyst you have deep insight into crime and criminal activity especially the field of "
            "online human trafficking. "
            "You are careful and precise and can compare adverts in the finest detail."
            "You are specifically looking for perpetrators who are using employment advertisements to exploit victims. "
        ),
    )
    prompt = """Please summarize the following text into distinct bullet points without losng any of the original content or context:"""
    chat_engine = create_chat_engine(index)
    attempt = 0
    max_retries = 3

    response = chat_engine.chat(prompt)
    formatted_response = response.response.strip()  # Remove leading/trailing whitespace
    result = [node, formatted_response]
    results.append(result)
    print(result)

gf = pd.DataFrame(results)
gf.columns = ["node", "suspicion_summary"]
gf = df[["advert", "more_suspicious"]].merge(
    gf, left_on="more_suspicious", right_on="node"
)
gf = gf.drop_duplicates()
gf[["advert", "suspicion_summary"]].to_csv("results/suspicion_summary.csv", index=False)
import matplotlib.pyplot as plt

plt.scatter(df["monitor_more_suspicious_rating"], df["more_suspicious_pagerank"])
plt.xlabel("Column1")
plt.ylabel("Column2")
plt.title("Scatter Plot of Column1 vs Column2")
plt.show()


list(pagerank_df_sample_1)
advert_urlb = advert_urls[index_b]
advert_b = advert_sample[advert_sample.post_url == advert_urlb]
documents = [
    Document(
        text=advert_a,
        metadata={"advert": "advert_a"},
    ),
    Document(
        text=advert_b,
        metadata={"advert": "advert_b"},
    ),
]
index = VectorStoreIndex.from_documents(documents, llm=llm)
comparison = compare_adverts(index, advert_prompt)
if comparison is not None:
    if comparison["most suspect"] == "advert_a":
        outcome = (index_a, index_b)
    elif comparison["most suspect"] == "advert_b":
        outcome = (index_b, index_a)
    else:
        outcome = ()
    results.append(outcome)
index_b += 1
