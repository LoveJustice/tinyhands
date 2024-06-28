import pandas as pd
from llama_index.core import Document
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    SentenceSplitter,
)
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import get_leaf_nodes, get_root_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.query_engine import RetrieverQueryEngine
import re
import ast

data = pd.read_csv("results/advert_comparison_cleaned.csv")


data_columns = list(data.columns)
list()
data = data.replace({"TRUE": 1, "FALSE": 0})
data = data.drop(index=0)
data.columns


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
for idx, feature in enumerate(features):
    red_flags[feature] = f"```Red Flag {idx}. " + feature + "```"


for idx, row in data.iterrows():
    identified_features = []
    for feature in features:
        if row[feature] == 1:
            identified_features.append(red_flags[feature])
        else:
            data.loc[idx, feature] = None

    story = f"""The advert with text ```{row['Unnamed 1']}``` is given a Monitor Rating of {row['Monitor Rating']} where 0 is not suspicious and 9 is likely fraudulent or fake.  
    and the Monitor Reason for giving this rating is {row['Monitor Reason']}.  This rating was given because the monitor highlighted the  following 
    features: {' AND '.join(identified_features)}. """
    stories.append(story)
    meta = {
        "idn": row["Unnamed 0"],
    }
    metadata.append(meta)

story = (
    "A monitor is a person who assesses a online recruitment adverts and provides a Likert-style rating as to the likelihood "
    "of this advert being used for the purposes of falsely luring respondents into trafficking.  The Likert scale"
    "ranges from 0 to 9, where 0 is not suspicious and 9 is likely fraudulent or fake.  The rating is known as the Monitor rating."
    "The Monitor also notes a reason for their rating."
    "Here is a list of key features a Monitor looks for in the advert:"
    "[```Recruiting young people who are still in school```",
    "```Paying more than the market rate for the skill level or type of job that they are hiring for```",
    "```Not mentioning any skill requirements```",
    "```Not mentioning the nature of the job```",
    "```Not mentioning the name or the location of the hiring business```",
    "```Paying the same salary for different job posts positions```",
    "```Hiring for an organization such as ESKOM who has publicly stated that they don't advertise job posts on social media```",
    "```Recruiting specifically females for a job that male or female applicants would qualify for```,",
    "```Unprofessional writing poor grammar spelling```",
    "```Recruiting models```",
    "```Changing from English to other languages in the middle of the post```",
    "```Using a suspicious email address```",
    "```Advertising for positions in several promises especially without detail```, ```Looks Legit```]",
    "When the Monitor has NO reason to suspect that the adverts is being used for the purposes of human trafficking,"
    "the option 'Looks Legit' is chosen.  However the Monitor HAS to choose one of these options.",
)
stories.append(story)
documents = []
for meta, document in zip(metadata, stories):
    documents.append(Document(text=document, metadata=meta))

node_parser = HierarchicalNodeParser.from_defaults()

nodes = node_parser.get_nodes_from_documents(documents)
len(nodes)


leaf_nodes = get_leaf_nodes(nodes)
len(leaf_nodes)
root_nodes = get_root_nodes(nodes)
len(root_nodes)
# define storage context

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


base_retriever = base_index.as_retriever(similarity_top_k=6)
retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=True)
# query_str = "What were some lessons learned from red-teaming?"
# query_str = "Can you tell me about the key concepts for safety finetuning"
advert = data.sample(1)["Unnamed 1"].values[0]
data.sample(1)["Unnamed 0"].values[0]
query_str = (
    f"Assistant please provide a Monitor rating and a Monitor reason for the following advert ```{advert}```"
    "without using your pretrained knowledge about human trafficking but only the documentation given to you."
    "Please provide your Monitor rating on an integer scale of 0 to 9, with 9 being the most likely to be used in human trafficking."
    "Also provide a reason for your Monitor rating.  This reason must also NOT be extracted from anywhere else but the documentation given to you."
    "You will also need to provide a list of ALL red flags that you have identified in the advert as per the documentation given to you."
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


for node in nodes:
    p = display_source_node(node, source_length=10000)

for node in base_nodes:
    display_source_node(node, source_length=10000)


query_engine = RetrieverQueryEngine.from_args(retriever)
base_query_engine = RetrieverQueryEngine.from_args(base_retriever)

response = query_engine.query(prompt)
print(response.response)
print(str(response))
base_response = base_query_engine.query(prompt)
import ast

ast.literal_eval(base_response.response)
base_response.response


rows = []
for idx, row in data.iterrows():
    row_entry = {}
    for feature in features:
        row_entry[feature] = 0
    advert = row["Unnamed 1"]
    print(advert)
    query_str = (
        f"Assistant please provide a Monitor rating and a Monitor reason for the following advert ```{advert}```"
        "without using your pretrained knowledge about human trafficking but only the documentation given to you."
        "Please provide your Monitor rating on an integer scale of 0 to 9, with 9 being the most likely to be used in human trafficking."
        "Also provide a reason for your Monitor rating.  This reason must also NOT be extracted from anywhere else but the documentation given to you."
        "You will also need to provide a list of ALL red flags that you have identified in the advert as per the documentation given to you."
        "Features can ONLY be one OR more of the following, don't make up new ones :"
        "[```Recruiting young people who are still in school```",
        "```Paying more than the market rate for the skill level or type of job that they are hiring for```",
        "```Not mentioning any skill requirements```",
        "```Not mentioning the nature of the job```",
        "```Not mentioning the name or the location of the hiring business```",
        "```Paying the same salary for different job posts positions```",
        "```Hiring for an organization such as ESKOM who has publicly stated that they don't advertise job posts on social media```",
        "```Recruiting specifically females for a job that male or female applicants would qualify for```,",
        "```Unprofessional writing poor grammar spelling```",
        "```Recruiting models```",
        "```Changing from English to other languages in the middle of the post```",
        "```Using a suspicious email address```",
        "```Advertising for positions in several promises especially without detail```, ```Looks Legit```]",
        "Provide your response in JSON format and ensure it can be parsed correctly."
        "Here is an example:"
        '{"Monitor rating": integer, "Monitor reason": "reasoning", "features": ["feature one", "feature two", ...]}',
    )
    prompt = " ".join(query_str)

    nodes = retriever.retrieve(prompt)
    base_nodes = base_retriever.retrieve(prompt)

    for node in nodes:
        p = display_source_node(node, source_length=10000)

    for node in base_nodes:
        display_source_node(node, source_length=10000)

    query_engine = RetrieverQueryEngine.from_args(retriever)
    base_query_engine = RetrieverQueryEngine.from_args(base_retriever)
    response = query_engine.query(prompt)
    base_response = base_query_engine.query(prompt)
    ast.literal_eval(base_response.response)
    response_dict = ast.literal_eval(base_response.response)
    for feature in response_dict["features"]:
        row_entry[feature] = 1
    row_entry["Monitor rating"] = response_dict["Monitor rating"]
    row_entry["Monitor reason"] = response_dict["Monitor reason"]
    row_entry["IDn"] = row["Unnamed 0"]
    row_entry["Advert"] = advert
    print(row_entry)
    rows.append(row_entry)

df = pd.DataFrame(rows)
df["Monitor rating"]
sf = data.merge(
    df[["IDn", "Monitor rating", "Monitor reason"]], left_on="Unnamed 0", right_on="IDn"
)
sf[["Monitor rating", "Monitor Rating"]]
df.to_csv("results/RAG_advert_monitoring.csv", index=False)
columns = [
    "IDn",
    "Advert",
    "Monitor rating",
    "Monitor reason",
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
df[columns].to_csv("results/RAG_advert_monitoring.csv", index=False)
