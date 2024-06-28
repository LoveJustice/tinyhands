import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.miscmodels.ordinal_model import OrderedModel

# Load your data
data = pd.read_csv("results/advert_comparison_cleaned.csv")


data_columns = list(data.columns)
list()
data = data.replace({"TRUE": 1, "FALSE": 0})
data = data.drop(index=0)
data.columns
import re

new_cols = [re.sub("\W+", " ", col).strip() for col in data_columns]
rename = {}
for new_col, col in zip(new_cols, data_columns):
    rename[col] = new_col
data.rename(columns=rename, inplace=True)
list(data)
features = [
    "Recruiting young people who are still in school",
    "Paying more than the market rate for the skill level or type of job that they are hiring for",
    "Not mentioning any skill requirements",
    "Not mentioning the nature of the job",
    "Not mentioning the name or the location of the hiring business",
    "Paying the same salary for different job posts positions",
    "Hiring for an organization such as ESKOM who has publicly stated that they don t advertise job posts on social media",
    "Recruiting specifically females for a job that male or female applicants would qualify for",
    "Unprofessional writing poor grammar spelling",
    "Recruiting models",
    "Changing from English to other languages in the middle of the post",
    "Using a suspicious email address",
    "Advertising for positions in several promises especially without detail",
    "Looks Legit",
]
stories = []
metadata = []
red_flags = {}
for feature in features:
    red_flags[feature] = "Red Flag 1. " + feature
for idx, row in data.iterrows():
    identified_features = []
    for feature in features:
        if row[feature] == 1:
            data.loc[idx, feature] = feature
            identified_features.append(red_flags[feature])
        else:
            data.loc[idx, feature] = None

    story = f"""The advert with text {row['Unnamed 1']} is given a Monitor Rating of {row['Monitor Rating']} where 0 is not suspicious and 9 is likely fraudulent or fake.  
    and the Monitor Reason for giving this rating is {row['Monitor Reason']}.  The following 
    red flags were observed: {' AND '.join(identified_features)}. """
    stories.append(story)
    meta = {
        "idn": row["Unnamed 0"],
    }
    metadata.append(meta)


data.to_csv("results/data_stories.csv", index=False)

from llama_index.core import Document

documents = []
for meta, document in zip(metadata, stories):
    documents.append(Document(text=document, metadata=meta))
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer

llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=128000)
memory = ChatMemoryBuffer.from_defaults(token_limit=64000)


def create_chat_engine(index):
    memory.reset()
    return index.as_chat_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "As a career forensic analyst you have deep insight into crime and criminal activity especially the field of "
            "online human trafficking. "
            "You are careful and precise and can compare adverts in the finest detail."
            "You are specifically looking for perpetrators who are using employment advertisements to exploit victims."
            "Apart from legitimate adverts you carefully consider these red flags when assessing an advert: "
            "[Recruiting young people who are still in school",
            "Paying more than the market rate for the skill level or type of job that they are hiring for",
            "Not mentioning any skill requirements",
            "Not mentioning the nature of the job",
            "Not mentioning the name or the location of the hiring business",
            "Paying the same salary for different job posts positions",
            "Hiring for an organization such as ESKOM who has publicly stated that they don t advertise job posts on social media",
            "Recruiting specifically females for a job that male or female applicants would qualify for",
            "Unprofessional writing poor grammar spelling",
            "Recruiting models",
            "Changing from English to other languages in the middle of the post",
            "Using a suspicious email address",
            "Advertising for positions in several promises especially without detail]",
        ),
    )


def create_query_engine(index):
    memory.reset()
    return index.as_query_engine(
        chat_mode="context",
        memory=memory,
        system_prompt=(
            "As a career forensic analyst you have deep insight into crime and criminal activity especially the field of "
            "online human trafficking. "
            "You are careful and precise and can compare adverts in the finest detail."
            "You are specifically looking for perpetrators who are using employment advertisements to exploit victims."
            "Apart from legitimate adverts you carefully consider these red flags when assessing an advert: "
            "[Recruiting young people who are still in school",
            "Paying more than the market rate for the skill level or type of job that they are hiring for",
            "Not mentioning any skill requirements",
            "Not mentioning the nature of the job",
            "Not mentioning the name or the location of the hiring business",
            "Paying the same salary for different job posts positions",
            "Hiring for an organization such as ESKOM who has publicly stated that they don t advertise job posts on social media",
            "Recruiting specifically females for a job that male or female applicants would qualify for",
            "Unprofessional writing poor grammar spelling",
            "Recruiting models",
            "Changing from English to other languages in the middle of the post",
            "Using a suspicious email address",
            "Advertising for positions in several promises especially without detail]",
        ),
    )


index = VectorStoreIndex.from_documents(documents, llm=llm)
chat_engine = create_chat_engine(index)

advert = data.sample(1)["Unnamed 1"].values[0]
prompt = (
    f"Assistant please provide a Monitor rating and a Monitor reason for the following advert ```{advert}```"
    "pretrained knowledge about human trafficking but only upon your own index."
    "Please provide you rating on an integer scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
    "Also provide a reason for your Monitor rating.  This reason must also NOT be extracted from anywhere else but the documentation given to you."
    "You will also need to provide red flags that you have identified in the advert that may indicate human trafficking as perthe documentation given to you."
    "Red flags can ONLY be one OR more of the following:"
    "[Recruiting young people who are still in school",
    "Paying more than the market rate for the skill level or type of job that they are hiring for",
    "Not mentioning any skill requirements",
    "Not mentioning the nature of the job",
    "Not mentioning the name or the location of the hiring business",
    "Paying the same salary for different job posts positions",
    "Hiring for an organization such as ESKOM who has publicly stated that they don t advertise job posts on social media",
    "Recruiting specifically females for a job that male or female applicants would qualify for",
    "Unprofessional writing poor grammar spelling",
    "Recruiting models",
    "Changing from English to other languages in the middle of the post",
    "Using a suspicious email address",
    "Advertising for positions in several promises especially without detail]",
    "When there are NO red flags, please indicate this by stating 'No red flags identified'."
    "Provide your response in JSON format and ensure it can be parsed correctly."
    "Here is an example:"
    '{{"rating": integer, "reason": "reasoning", "red flags": ["red flag 1", "red flag 2", etc]}}',
)
memory.reset()
response = chat_engine.chat(prompt)


from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    SentenceSplitter,
)

node_parser = HierarchicalNodeParser.from_defaults()

nodes = node_parser.get_nodes_from_documents(documents)
len(nodes)
from llama_index.core.node_parser import get_leaf_nodes, get_root_nodes

leaf_nodes = get_leaf_nodes(nodes)
len(leaf_nodes)
root_nodes = get_root_nodes(nodes)
len(root_nodes)

# define storage context
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI

docstore = SimpleDocumentStore()

# insert nodes into docstore
docstore.add_documents(nodes)

# define storage context (will include vector store by default too)
storage_context = StorageContext.from_defaults(docstore=docstore)

llm = OpenAI(model="gpt-4o")
## Load index into vector index
from llama_index.core import VectorStoreIndex

base_index = VectorStoreIndex(
    leaf_nodes,
    storage_context=storage_context,
)

from llama_index.core.retrievers import AutoMergingRetriever

base_retriever = base_index.as_retriever(similarity_top_k=6)
retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=True)
# query_str = "What were some lessons learned from red-teaming?"
# query_str = "Can you tell me about the key concepts for safety finetuning"
advert = data.sample(1)["Unnamed 1"].values[0]
query_str = (
    f"Assistant please provide a Monitor rating and a Monitor reason for the following advert ```{advert}```"
    "pretrained knowledge about human trafficking but only upon your own index."
    "Please provide you rating on an integer scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
    "Also provide a reason for your Monitor rating.  This reason must also NOT be extracted from anywhere else but the documentation given to you."
    "You will also need to provide red flags that you have identified in the advert that may indicate human trafficking as perthe documentation given to you."
    "Red flags can ONLY be one OR more of the following, don't make up new ones and do not blend any together as you see fit:"
    "[Recruiting young people who are still in school",
    "Paying more than the market rate for the skill level or type of job that they are hiring for",
    "Not mentioning any skill requirements",
    "Not mentioning the nature of the job",
    "Not mentioning the name or the location of the hiring business",
    "Paying the same salary for different job posts positions",
    "Hiring for an organization such as ESKOM who has publicly stated that they don t advertise job posts on social media",
    "Recruiting specifically females for a job that male or female applicants would qualify for",
    "Unprofessional writing poor grammar spelling",
    "Recruiting models",
    "Changing from English to other languages in the middle of the post",
    "Using a suspicious email address",
    "Advertising for positions in several promises especially without detail]",
    "When there are NO red flags, please indicate this by stating 'No red flags identified'."
    "Provide your response in JSON format and ensure it can be parsed correctly."
    "Here is an example:"
    '{"Monitor rating": integer, "Monitor reason": "reasoning", "red flags": ["red flag 1", "red flag 2", etc]}',
)
prompt = " ".join(query_str)

nodes = retriever.retrieve(prompt)
base_nodes = base_retriever.retrieve(prompt)

from llama_index.core.response.notebook_utils import display_source_node

for node in nodes:
    p = display_source_node(node, source_length=10000)

for node in base_nodes:
    display_source_node(node, source_length=10000)

from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(retriever)
base_query_engine = RetrieverQueryEngine.from_args(base_retriever)

response = query_engine.query(prompt)
print(response.response)
