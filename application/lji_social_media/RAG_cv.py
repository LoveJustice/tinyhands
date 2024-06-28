import pandas as pd
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
import json


llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=128000)
memory = ChatMemoryBuffer.from_defaults(token_limit=64000)
comparison = pd.read_csv("results/comparison.csv")
rename = {
    "advert_y": "text",
    "Rating 1 - 10 (10 is most likely to be HT)": "rating",
    "Reason": "reason",
}
comparison.rename(columns=rename, inplace=True)
list(comparison)
comparison.shape
lji_prompt = (
    "Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
    "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
    "Also provide a reason for your rating."
    "Please provide your response in JSON format and ensure it can be parsed correctly."
    "Here is an example:"
    '{{"rating": integer, "reason": "reasoning"}}"'
)


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


def create_cv_documents(data) -> list:
    documents = []
    for i, row_i in data.iterrows():
        text_entry = (
            f"This advert text  ```{row_i['text']}``` scores {row_i['rating']} with this reason ```{row_i['reason']}```,"
            f" when evaluated for being fake, fraudulent or a scam in the business of human trafficking."
        )

        documents.append(
            Document(
                text=text_entry,
                metadata={"urlA": row_i["post_url"]},
            )
        )
    return documents


documents = []
for i, row_i in comparison.iterrows():
    text_entry = (
        f"This advert text  ```{row_i['text']}``` scores {row_i['rating']} with this reason ```{row_i['reason']}```,"
        f" when evaluated for being fake, fraudulent or a scam in the business of human trafficking."
    )

    documents.append(
        Document(
            text=text_entry,
            metadata={"urlA": row_i["post_url"]},
        )
    )
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    chat_engine = create_chat_engine(index)


ratings = []
for idx in range(comparison.shape[0]):
    data = comparison.drop([idx]).copy()
    cv_documents = create_cv_documents(data)
    memory.reset()
    cv_index = VectorStoreIndex.from_documents(cv_documents, llm=llm)
    chat_engine = create_chat_engine(cv_index)
    advert = comparison.loc[idx, "text"]
    lji_prompt = (
        f"Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
        "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
        "Also provide a reason for your rating."
        "Please provide your response in JSON format and ensure it can be parsed correctly."
        "Here is an example:"
        '{"rating": integer, "reason": "reasoning"}"'
    )
    response = chat_engine.chat(lji_prompt)
    print(response.response)
    formatted_response = response.response.strip()  # Remove leading/trailing whitespace

    s = json.loads(formatted_response)
    ratings.append(s)

cv_ratings = pd.DataFrame(ratings)
rename = {"rating": "rating_cv", "reason": "reason_cv"}
cv_ratings.rename(columns=rename, inplace=True)
comparison_cv = comparison.join(cv_ratings)
comparison_cv.to_csv("results/lji_comparison_cv.csv", index=False)
list(comparison_cv)
comparison_cv[["rating", "rating_cv", "reason", "reason_cv"]]
comparison_cv[["rating", "rating_cv"]]


ratings = []
for idx in range(comparison.shape[0]):
    data = comparison.drop([idx]).copy()
    cv_documents = create_cv_documents(data)
    memory.reset()
    cv_index = VectorStoreIndex.from_documents(cv_documents, llm=llm)
    chat_engine = create_chat_engine(cv_index)
    advert = comparison.loc[idx, "text"]
    prompt = (
        f"Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
        "Please provide you rating on an integer scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
        "Also provide a reason for your rating."
        "When evaluating an advert for being fake, fraudulent or having evidence of being used in the"
        "process of human trafficking, also consider any or all of the"
        "following well-known tell-tale signs:"
        "1. Targeting Vulnerable Populations"
        "2. Vague Job Descriptions and Promises"
        "3. Promises of High Salaries and Attractive Benefits"
        "4. Urgency and Immediate Availability"
        "5. Lack of Professionalism"
        "6. Suspicious Application Processes"
        " Also include the above in your verdict and explanation."
        "Provide your response in JSON format and ensure it can be parsed correctly."
        "Here is an example:"
        '{{"rating": integer, "reason": "reasoning"}}'
    )
    response = chat_engine.chat(prompt)
    print(response.response)
    formatted_response = response.response.strip()  # Remove leading/trailing whitespace

    s = json.loads(formatted_response)
    ratings.append(s)

cv_ratings = pd.DataFrame(ratings)
rename = {"rating": "rating_cv", "reason": "reason_cv"}
cv_ratings.rename(columns=rename, inplace=True)
comparison_cv = comparison.join(cv_ratings)
comparison_cv.to_csv("results/gptlji_comparison_cv.csv", index=False)
list(comparison_cv)
comparison_cv[["rating", "rating_cv", "reason", "reason_cv"]]
comparison_cv[["rating", "rating_cv"]]


ratings = []
for idx in range(comparison.shape[0]):
    data = comparison.drop([idx]).copy()
    cv_documents = create_cv_documents(data)
    memory.reset()
    cv_index = VectorStoreIndex.from_documents(cv_documents, llm=llm)
    chat_engine = create_chat_engine(cv_index)
    advert = comparison.loc[idx, "text"]
    prompt = (
        f"Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
        "Please provide you rating on an integer scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
        "Also provide a reason for your rating."
        "When evaluating an advert for being fake, fraudulent or having evidence of being used in the"
        "process of human trafficking, also consider any or all of the"
        "following well-known tell-tale signs:"
        "1. Targeting Vulnerable Populations"
        "2. Vague Job Descriptions and Promises"
        "3. Promises of High Salaries and Attractive Benefits"
        "4. Urgency and Immediate Availability"
        "5. Lack of Professionalism"
        "6. Suspicious Application Processes"
        " Also include the above in your verdict and explanation."
        "Provide your response in JSON format and ensure it can be parsed correctly."
        "Here is an example:"
        '{{"rating": integer, "reason": "reasoning"}}'
    )
    response = chat_engine.chat(prompt)
    print(response.response)
    formatted_response = response.response.strip()  # Remove leading/trailing whitespace

    s = json.loads(formatted_response)
    ratings.append(s)

cv_ratings = pd.DataFrame(ratings)
rename = {"rating": "rating_cv", "reason": "reason_cv"}
cv_ratings.rename(columns=rename, inplace=True)
comparison_cv = comparison.join(cv_ratings)
comparison_cv.to_csv("results/gpt_comparison_cv.csv", index=False)
list(comparison_cv)
comparison_cv[["rating", "rating_cv", "reason", "reason_cv"]]
comparison_cv[["rating", "rating_cv"]]

# Combine everything
GPT_adverts_ratings = pd.read_csv("results/GPT_adverts_ratings.csv")
gpt_comparison_cv = pd.read_csv("results/gpt_comparison_cv.csv")
lji_comparison_cv = pd.read_csv("results/lji_comparison_cv.csv")
gptlji_comparison_cv = pd.read_csv("results/gptlji_comparison_cv.csv")
list(gpt_comparison_cv)
list(GPT_adverts_ratings)
list(lji_comparison_cv)
list(gptlji_comparison_cv)
merged_comparisons = comparison[["IDn", "rating", "reason"]].merge(
    GPT_adverts_ratings[["IDn", "GPT_advert_rating", "GPT_advert_reason"]],
    left_on="IDn",
    right_on="IDn",
)
merged_comparisons = merged_comparisons.merge(
    lji_comparison_cv[["IDn", "rating_cv", "reason_cv"]], left_on="IDn", right_on="IDn"
)
rename = {
    "rating_cv": "LJIRAG_advert_rating",
    "reason_cv": "LJIRAG_advert_reason",
}
merged_comparisons.rename(columns=rename, inplace=True)

merged_comparisons = merged_comparisons.merge(
    gptlji_comparison_cv[["IDn", "rating_cv", "reason_cv"]],
    left_on="IDn",
    right_on="IDn",
)

rename = {
    "rating_cv": "GPTLJI_advert_rating",
    "reason_cv": "GPTLJI_advert_reason",
}
merged_comparisons.rename(columns=rename, inplace=True)
merged_comparisons.to_csv("results/merged_comparisons.csv", index=False)

LJIRAG_advert_rating = merged_comparisons["LJIRAG_advert_rating"].to_list()
GPT_advert_rating = merged_comparisons["GPT_advert_rating"].to_list()
GPTLJI_advert_rating = merged_comparisons["GPTLJI_advert_rating"].to_list()
MONITORS_advert_rating = merged_comparisons["rating"].to_list()


# Visual and quantitative analysis of the ratings
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import matplotlib.pyplot as plt
import seaborn as sns

# Sample data


# Convert lists to DataFrame
df = pd.DataFrame(
    {
        "MONITORS_advert_rating": MONITORS_advert_rating,
        "LJIRAG_advert_rating": LJIRAG_advert_rating,
        "GPT_advert_rating": GPT_advert_rating,
        "GPTLJI_advert_rating": GPTLJI_advert_rating,
    }
)

# Calculate correlation coefficients
correlations = {
    "Pearson": df.corr(method="pearson"),
    "Spearman": df.corr(method="spearman"),
    "Kendall": df.corr(method="kendall"),
}

for method, corr_df in correlations.items():
    corr_df.to_csv(f"{method}_correlation.csv")


# Rank adverts using gptlji_comparison_cv

import re


def try_fix_json(broken_json):
    # Example fix: remove trailing commas before closing brackets or braces
    try:
        fixed_json = re.sub(r",\s*([}\]])", r"\1", broken_json)
        return fixed_json
    except Exception as e:
        print("Failed to fix JSON:", e)
        return None


def compare_adverts(chat_engine, prompt, max_retries=7):
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


list(comparison)
documents = []
for i, row_i in comparison.iterrows():
    for j, row_j in comparison.iterrows():
        if row_i["rating"] > row_j["rating"]:
            text_entry = (
                f"This advert text A ```{row_i['text']}``` scores {row_i['rating']} with this reason ```{row_i['reason']}```,"
                f" and is considered to be more likely to be either fake, fraudulent or a scam in the business of human trafficking, than  advert B"
                f"```{row_j['text']}``` which scores {row_j['rating']} with this reason ```{row_j['reason']}```."
            )

            documents.append(
                Document(
                    text=text_entry,
                    metadata={"urlA": row_i["post_url"], "urlB": row_j["post_url"]},
                )
            )
        if row_i["rating"] == row_j["rating"]:
            text_entry = (
                f"This advert text A ```{row_i['text']}``` scores {row_i['rating']} with this reason ```{row_i['reason']}```,"
                f" and is considered to be equally likely to be either fake, fraudulent or a scam in the business of human trafficking, than  advert B"
                f"```{row_j['text']}```, which scores {row_j['rating']} with this reason ```{row_j['reason']}```."
            )

index = VectorStoreIndex.from_documents(documents, llm=llm)
chat_engine = create_chat_engine(index)

advert_urls = comparison.post_url.to_list()

results = []
reasons = []

for index_a in range(len(advert_urls) - 1, -1, -1):
    advert_urla = advert_urls[index_a]
    advert_a = comparison[comparison.post_url == advert_urla]["text"].values[0]
    print(advert_a)

    for index_b in range(index_a - 1, -1, -1):
        advert_urlb = advert_urls[index_b]
        advert_b = comparison[comparison.post_url == advert_urlb]["text"].values[0]

        advert_prompt = (
            f"Assistant, Here is advert_a: ```{advert_a}```"
            f"And here is advert_b: ```{advert_b}``` Which of these two is more likely to be either fake, fraudulent or a scam in the business of human trafficking and why?"
            f"When evaluating an advert for being fake, fraudulent or having evidence of being used in the"
            f"process of human trafficking, also consider any or all of the"
            f"following well-known tell-tale signs:"
            f"1. Targeting Vulnerable Populations"
            "2. Vague Job Descriptions and Promises"
            "3. Promises of High Salaries and Attractive Benefits"
            "4. Urgency and Immediate Availability"
            "5. Lack of Professionalism"
            "6. Suspicious Application Processes"
            " Also include the above in your verdict and explanation."
            "Please provide your response in the following JSON format and ensure it can be parsed correctly:"
            '{"most_suspect": "advert_a" or "advert_b" or "neither"'
            '"reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."}'
        )
        memory.reset()
        advert_comparison = compare_adverts(chat_engine, advert_prompt)
        if advert_comparison is not None:
            if advert_comparison["most_suspect"] == "advert_a":
                outcome = (index_b, index_a)
                results.append(outcome)
            elif advert_comparison["most_suspect"] == "advert_b":
                outcome = (index_a, index_b)
                results.append(outcome)
            elif advert_comparison["most_suspect"] == "neither":
                results.append((index_a, index_b))
                results.append((index_b, index_a))
            reason = [advert_a, advert_b, advert_comparison["reasoning"]]
            reasons.append(reason)

import networkx as nx

edges = [t for t in results if t]
# reversed_edges = [(m, n) for n, m in edges]
# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph (relationship is (n)<-[]-(m))
G.add_edges_from(edges)
nx.google_matrix(G)
pagerank = nx.pagerank(G)
pageranks = []
for i in range(len(pagerank)):
    pageranks.append(pagerank[i])
merged_comparisons.to_csv("results/merged_comparisons.csv", index=False)
merged_comparisons = pd.read_csv("results/merged_comparisons.csv")
merged_comparisons["gptlji_pagerank"] = pageranks
merged_comparisons.to_csv("results/merged_comparisons.csv", index=False)
# Get the top 5 most suspicious adverts


#
adverts = pd.read_csv("results/adverts.csv")

adverts[~adverts.IDn.isin(comparison.IDn)].sample(100).to_csv(
    "results/adverts_sample.csv", index=False
)

numbers = list(range(len(advert_urls)))
unique_tuples = []

for i in range(len(numbers)):
    for j in range(i + 1, len(numbers)):
        unique_tuples.append((numbers[i], numbers[j]))

print(unique_tuples)

import random

# Example list


# Shuffle the list
random.shuffle(unique_tuples)


results = []
reasons = []

for pair in unique_tuples:
    index_a = pair[0]
    index_b = pair[1]
    advert_urla = advert_urls[index_a]
    advert_a = comparison[comparison.post_url == advert_urla]["text"].values[0]
    print(advert_a)
    advert_urlb = advert_urls[index_b]
    advert_b = comparison[comparison.post_url == advert_urlb]["text"].values[0]

    advert_prompt = (
        f"Assistant, Here is advert_a: ```{advert_a}```"
        f"And here is advert_b: ```{advert_b}``` Which of these two is more likely to be either fake, fraudulent or a scam in the business of human trafficking and why?"
        f"When evaluating an advert for being fake, fraudulent or having evidence of being used in the"
        f"process of human trafficking, also consider any or all of the"
        f"following well-known tell-tale signs:"
        f"1. Targeting Vulnerable Populations"
        "2. Vague Job Descriptions and Promises"
        "3. Promises of High Salaries and Attractive Benefits"
        "4. Urgency and Immediate Availability"
        "5. Lack of Professionalism"
        "6. Suspicious Application Processes"
        " Also include the above in your verdict and explanation."
        "Please do not make anything up. If there is no evidence of suspicious activity in either advertisement, explicitly state this conclusion."
        "Please provide your response in the following JSON format and ensure it can be parsed correctly:"
        '{"most_suspect": "advert_a" or "advert_b" or "neither"'
        '"reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."}'
    )
    memory.reset()
    advert_comparison = compare_adverts(chat_engine, advert_prompt)
    if advert_comparison is not None:
        if advert_comparison["most_suspect"] == "advert_a":
            outcome = (index_b, index_a)
            results.append(outcome)
        elif advert_comparison["most_suspect"] == "advert_b":
            outcome = (index_a, index_b)
            results.append(outcome)
        elif advert_comparison["most_suspect"] == "neither":
            results.append((index_a, index_b))
            results.append((index_b, index_a))
        reason = [advert_a, advert_b, advert_comparison["reasoning"]]
        reasons.append(reason)

random.shuffle(unique_tuples)

for pair in unique_tuples:
    index_a = pair[1]
    index_b = pair[0]
    advert_urla = advert_urls[index_a]
    advert_a = comparison[comparison.post_url == advert_urla]["text"].values[0]
    print(advert_a)
    advert_urlb = advert_urls[index_b]
    advert_b = comparison[comparison.post_url == advert_urlb]["text"].values[0]

    advert_prompt = (
        f"Assistant, Here is advert_a: ```{advert_a}```"
        f"And here is advert_b: ```{advert_b}``` Which of these two is more likely to be either fake, fraudulent or a scam in the business of human trafficking and why?"
        f"When evaluating an advert for being fake, fraudulent or having evidence of being used in the"
        f"process of human trafficking, also consider any or all of the"
        f"following well-known tell-tale signs:"
        f"1. Targeting Vulnerable Populations"
        "2. Vague Job Descriptions and Promises"
        "3. Promises of High Salaries and Attractive Benefits"
        "4. Urgency and Immediate Availability"
        "5. Lack of Professionalism"
        "6. Suspicious Application Processes"
        " Also include the above in your verdict and explanation."
        "Please do not make anything up. If there is no evidence of suspicious activity in either advertisement, explicitly state this conclusion."
        "Please provide your response in the following JSON format and ensure it can be parsed correctly:"
        '{"most_suspect": "advert_a" or "advert_b" or "neither"'
        '"reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."}'
    )
    memory.reset()
    advert_comparison = compare_adverts(chat_engine, advert_prompt)
    if advert_comparison is not None:
        if advert_comparison["most_suspect"] == "advert_a":
            outcome = (index_b, index_a)
            results.append(outcome)
        elif advert_comparison["most_suspect"] == "advert_b":
            outcome = (index_a, index_b)
            results.append(outcome)
        elif advert_comparison["most_suspect"] == "neither":
            results.append((index_a, index_b))
            results.append((index_b, index_a))
        reason = [advert_a, advert_b, advert_comparison["reasoning"]]
        reasons.append(reason)


# Ratings to ranking
list(merged_comparisons)
# merged_comparisons['GPT_advert_rating'].loc[0]


def generate_edges_from_ratings(unique_tuples, ratings):
    edges = []
    for pair in unique_tuples:
        if ratings.loc[pair[0]] < ratings.loc[pair[1]]:
            edges.append(
                (
                    pair[0],
                    pair[1],
                )
            )
        if ratings.loc[pair[0]] > ratings.loc[pair[1]]:
            edges.append(
                (
                    pair[1],
                    pair[0],
                )
            )
        if ratings.loc[pair[0]] == ratings.loc[pair[1]]:
            edges.append(
                (
                    pair[0],
                    pair[1],
                )
            )

    return edges


GPT_advert_edges = generate_edges_from_ratings(
    unique_tuples, merged_comparisons["GPT_advert_rating"]
)
edges = [t for t in GPT_advert_edges if t]
G = nx.DiGraph()
G.add_edges_from(edges)
nx.google_matrix(G)
pagerank = nx.pagerank(G)
merged_comparisons["GPT_advert_rank"] = pagerank
list(merged_comparisons)
LJI_advert_edges = generate_edges_from_ratings(
    unique_tuples, merged_comparisons["rating"]
)
LJI_advert_edges.extend(edges)
G = nx.DiGraph()
G.add_edges_from(LJI_advert_edges)
nx.google_matrix(G)
pagerank = nx.pagerank(G)

merged_comparisons["LJI_GPT_advert_rank"] = pagerank
merged_comparisons.to_csv("results/merged_comparisons.csv", index=False)
