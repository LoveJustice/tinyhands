import pandas as pd
import streamlit as st
from llama_index.core import Settings
from llama_index.core import SimpleKeywordTableIndex, VectorStoreIndex
from llama_index.core import QueryBundle
from typing import List
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from ast import literal_eval
from llama_index.core import SummaryIndex
from llama_index.core.query_engine import ToolRetrieverRouterQueryEngine
from llama_index.core.objects import ObjectIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

# Retrievers
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)

Settings.chunk_size = 1024


class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableSimpleRetriever,
        mode: str = "AND",
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        keyword_nodes = self._keyword_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes


def generate_monitor_rating(query_engine, advert_text):
    response = query_engine.query(
        f"""As an experiences officed investigating fraudulent and harmful online recruitment adverts, what monitor rating will the following advert {advert_text} most likely receive?  
        Carefully understand and precisely follow the examples as laid out in the advert_guide.  Do not rely on you own understanding, or 
    pretrained knowledge.  Provide your answer using this JSON template {{\"monitor_rating\":integer}}:"""
    )
    # print(response)
    return literal_eval(response.response)["monitor_rating"]
    # define custom retriever


columns = [
    "Monitor Rating",
    "Recruiting young people who are still in school",
    "Paying more than the market rate for the skill level or type of job that they are hiring for",
    "Not mentioning any skill requirements",
    "Not mentioning the nature of the job",
    "Not mentioning the name or the location of the hiring business",
    "Paying the same salary for different job posts / positions",
    "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media",
    "Recruiting specifically females for a job that male or female applicants would qualify for",
    "Unprofessional writing (poor grammar / spelling)",
    "Recruiting models",
    "Changing from English to other languages in the middle of the post",
    "Using a suspicious email address",
    "Advertising for positions in several promises (especially without detail)",
    "Looks Legit",
]
adverts_sample = pd.read_csv(
    "~/github_repos/tinyhands/application/lji_social_media/results/advert_comparison_cleaned.csv"
)
paper = "~/github_repos/tinyhands/application/lji_social_media/docs/advert_guides.pdf"
# load documents
documents = SimpleDirectoryReader(input_files=[paper]).load_data()
nodes = Settings.node_parser.get_nodes_from_documents(documents)
# initialize storage context (by default it's in-memory)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)
summary_index = SummaryIndex(nodes, storage_context=storage_context)
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
list_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize", use_async=True
)
vector_query_engine = vector_index.as_query_engine(
    response_mode="tree_summarize", use_async=True
)

list_tool = QueryEngineTool.from_defaults(
    query_engine=list_query_engine,
    description="Useful for extracting SO's for an advert.",
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=("Useful for retrieving a Monitor Rating."),
)
obj_index = ObjectIndex.from_objects(
    [list_tool, vector_tool],
    index_cls=VectorStoreIndex,
)

query_engine = ToolRetrieverRouterQueryEngine(obj_index.as_retriever())


Settings.llm = OpenAI(temperature=0, model="gpt-4-turbo", max_tokens=128000)


advert_text = adverts_sample["advert"].sample(1).values[0]


response = query_engine.query(
    f"As a seasoned anti-human trafficking officer you stick to making observations (standardized observation) that are strictly "
    f"from the list as provided in the advert_guide.  "
    f"Which standardized observations can you from the following advert {advert_text}?  "
    f"Please provide your carefully crafted list in a json format."
)
print(response)
literal_eval(response.response)
advert_text = adverts_sample[:5]
answers = []


def create_query_str(advert):
    return (
        f"As a seasoned anti-human trafficking officer you stick to making observations (standardized observation) that are strictly "
        f"from the list as provided in the advert_guide.  "
        f"Which standardized observations can you from the following advert {advert}?  "
        f"Please provide your carefully crafted list  STRICTLY in this sample json format:"
        '{"Recruiting young people who are still in school": 0 or 1, '
        '"Paying more than the market rate for the skill level or type of job that they are hiring for": 0 or 1, '
        '"Not mentioning any skill requirements":0 or 1 '
        '"Not mentioning the nature of the job":0 or 1 '
        '"Not mentioning the name or the location of the hiring business":0 or 1'
        '"Paying the same salary for different job posts / positions": 0 or 1 '
        '"Hiring for an organization (such as ESKOM) who has publicly stated that they don\'t advertise job posts on social media": 0 or 1'
        '"Recruiting specifically females for a job that male or female applicants would qualify for": 0 or 1'
        '"Unprofessional writing (poor grammar / spelling)": 0 or 1'
        '"Recruiting models": 0 or 1'
        '"Changing from English to other languages in the middle of the post": 0 or 1'
        '"Using a suspicious email address": 0 or 1'
        '"Advertising for positions in several promises (especially without detail)": 0 or 1'
        '"Looks Legit": 0 or 1}'
    )


standardized_observations = []
monitor_ratings = []
list(adverts_sample)
from time import sleep

for idx, row in adverts_sample.iterrows():
    sleep(5)
    advert_text = row["advert"]
    query_str = create_query_str(advert_text)
    response = query_engine.query(query_str)
    observation = literal_eval(response.response)
    standardized_observations.append(observation)
    monitor_rating = generate_monitor_rating(query_engine, advert_text)
    # print(response)
    monitor_ratings.append(monitor_rating)
    print(row["IDn"], row["Monitor Rating"], monitor_rating, observation)

analysis = pd.DataFrame(standardized_observations)
analysis["llm_score"] = monitor_ratings
analysis.to_csv("results/adverts_20_analysis.csv", index=False)
analysis.fillna(0, inplace=True)
df = analysis.merge(
    adverts_sample[
        [
            "IDn",
            "advert",
            "Monitor Rating",
        ]
    ],
    left_index=True,
    right_index=True,
)

list(analysis)
list(adverts_sample)
for col in columns:
    df[col] = df[col].astype(int)
df.to_csv("results/adverts_20_analysis.csv", index=False)
adverts_za_sample_scored = pd.read_csv("results/adverts_za_20_sample_scored.csv")
list(adverts_za_sample_scored)
list(df)
df["llm_score"] = monitor_ratings
df.drop(columns=["monitor_rating", "Monitor Rating"], inplace=True)
df = df[
    [
        "IDn",
        "advert",
        "llm_score",
        "Recruiting young people who are still in school",
        "Paying more than the market rate for the skill level or type of job that they are hiring for",
        "Not mentioning any skill requirements",
        "Not mentioning the nature of the job",
        "Not mentioning the name or the location of the hiring business",
        "Paying the same salary for different job posts / positions",
        "Hiring for an organization (such as ESKOM) who has publicly stated that they don't advertise job posts on social media",
        "Recruiting specifically females for a job that male or female applicants would qualify for",
        "Unprofessional writing (poor grammar / spelling)",
        "Recruiting models",
        "Changing from English to other languages in the middle of the post",
        "Using a suspicious email address",
        "Advertising for positions in several promises (especially without detail)",
        "Looks Legit",
        "Advertising for positions in several provinces (especially without detail)",
    ]
]
# The dataframe contains dictionary-like strings. We need to convert these into actual dictionaries.
df = df.merge(adverts_za_sample_scored[["IDn", "Scoring", "Comments"]], on="IDn")
df.rename(
    columns={"Scoring": "monitor_score", "Comments": "monitor_comments"}, inplace=True
)
df.to_csv("results/adverts_za_sample_scored.csv", index=False)
# Convert dictionary-like strings to actual dictionaries

# Flatten the list of dictionaries into a single dataframe
flattened_data = []
for index, row in df.iterrows():
    for column in df.columns:
        if row[column] is not None:
            flattened_data.append(row[column])

# Create the final dataframe with 'observation_number' and 'observation_description' columns
final_df = pd.DataFrame(flattened_data)
