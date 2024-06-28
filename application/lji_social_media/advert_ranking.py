import pandas as pd
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

# Comparison function
import json
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

adverts = pd.read_csv("results/adverts.csv")
list(adverts)


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


def get_indeces(comparison, idx_a, idx_b):
    if comparison["most suspect"] == "advert_a":
        winner_idx, loser_idx, next_id = idx_a, idx_b, idx_b + 1
    elif comparison["most suspect"] == "advert_b":
        winner_idx, loser_idx, next_id = idx_b, idx_a, idx_b + 1
    else:
        winner_idx, loser_idx, next_id = idx_a, idx_b, idx_b + 1
    return winner_idx, loser_idx, next_id


def create_advert_prompt(IDn_a, IDn_b):
    return """Assistant, please examine the two documents with metadata IDs {IDn_a} (advert_a) and {IDn_b} (advert_b). Both documents are employment advertisements. Your task is to evaluate which advertisement is more likely to be associated with human trafficking by misrepresenting job opportunities for the purpose of exploiting victims. Determine whether one, both, or neither of these advertisements is suspect in this context.
If an advertisement does not seem to be aimed at employment exploitation, specify this clearly and then do not express an opinion on suspicion..
Your analysis should be thorough, with a focus on aspects such as the language used, the nature of the job offered, and any discrepancies or unusual elements in the advertisements.
Be consistent, objective, precise, and detailed in your evaluation.
If there is no evidence of suspicious activity in either advertisement, explicitly state this conclusion.
Do not make up any conclusion.

Please provide your response in the following JSON format:
{{
  "most suspect": "advert_a" or "advert_b" or "neither",
  "reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."
}}"""


query_str = """Assistant, please examine the two documents with metadata IDs {IDn_a} (advert_a) and {IDn_b} (advert_b). Both documents are employment advertisements. Your task is to evaluate which advertisement is more likely to be associated with human trafficking by misrepresenting job opportunities for the purpose of exploiting victims. Determine whether one, both, or neither of these advertisements is suspect in this context.
If an advertisement does not seem to be aimed at employment exploitation, specify this clearly.
Your analysis should be thorough, with a focus on aspects such as the language used, the nature of the job offered, and any discrepancies or unusual elements in the advertisements. Be consistent, objective, precise, and detailed in your evaluation. If there is no evidence of suspicious activity in either advertisement, explicitly state this conclusion.

Please provide your response in the following JSON format:
{{
  "most suspect": "advert_a" or "advert_b" or "neither",
  "reasoning": "Explain your reasoning, citing specific features of the advertisement that led to your conclusion."
}}"""


def compare_adverts(index, prompt, max_retries=3):
    chat_engine = create_chat_engine(index)
    attempt = 0
    while attempt < max_retries:
        response = chat_engine.chat(prompt)
        try:
            return json.loads(response.response)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt + 1} failed with JSON Decode Error:", e)
            print("Response received:", response.response)
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


llm = OpenAI(temperature=0, model="gpt-4-32k-0613")

memory = ChatMemoryBuffer.from_defaults(token_limit=32000)

idx_a = 0
idx_b = 1
IDn_a = adverts["IDn"][idx_a]
IDn_b = adverts["IDn"][idx_b]

memory.reset()
advert_prompt = create_advert_prompt(IDn_a, IDn_b)
documents = [
    Document(
        text=adverts["advert"][idx_a], metadata={"IDn": str(adverts["IDn"][idx_a])}
    ),
    Document(
        text=adverts["advert"][idx_b], metadata={"IDn": str(adverts["IDn"][idx_b])}
    ),
]

index = VectorStoreIndex.from_documents(documents, llm=llm)


# Initial comparison between the first two adverts
comparison = compare_adverts(index, advert_prompt)
winner_idx, loser_idx, next_id = get_indeces(comparison, idx_a, idx_b)
winner_idn, loser_idn = get_ids(comparison, IDn_a, IDn_b)
parameters = {
    "winner_idn": winner_idn,
    "loser_idn": loser_idn,
    "reason": comparison["reasoning"],
}
query = """MATCH (loser:Posting), (winner:Posting) WHERE ID(loser)=$loser_idn AND ID(winner)=$winner_idn WITH loser, winner
MERGE (winner)<-[:IS_MORE_SUSPICIOUS {reason:$reason}]-(loser)"""
execute_neo4j_query(query, parameters)
print(comparison["reasoning"])
for i in range(2, len(adverts)):
    IDn_a = adverts["IDn"][winner_idx]
    IDn_b = adverts["IDn"][next_id]
    advert_prompt = create_advert_prompt(IDn_a, IDn_b)
    documents = [
        Document(
            text=adverts["advert"][winner_idx],
            metadata={"IDn": str(adverts["IDn"][winner_idx])},
        ),
        Document(
            text=adverts["advert"][next_id],
            metadata={"IDn": str(adverts["IDn"][next_id])},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    winner_idx, loser_idx, next_id = get_indeces(comparison, winner_idx, next_id)
    winner_idn, loser_idn = get_ids(comparison, IDn_a, IDn_b)
    parameters = {
        "winner_idn": winner_idn,
        "loser_idn": loser_idn,
        "reason": comparison["reasoning"],
    }
    print(parameters)
    execute_neo4j_query(query, parameters)
    print(f"Winner: {winner_idx}, Loser: {loser_idx}", comparison)

# -Winner Reboot----------------------------------------------------------------------------------------
while max(winner_idx, next_id) < len(adverts):
    IDn_a = adverts["IDn"][winner_idx]
    IDn_b = adverts["IDn"][next_id]
    advert_prompt = create_advert_prompt(IDn_a, IDn_b)
    documents = [
        Document(
            text=adverts["advert"][winner_idx],
            metadata={"IDn": str(adverts["IDn"][winner_idx])},
        ),
        Document(
            text=adverts["advert"][next_id],
            metadata={"IDn": str(adverts["IDn"][next_id])},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    winner_idx, loser_idx, next_id = get_indeces(comparison, winner_idx, next_id)
    winner_idn, loser_idn = get_ids(comparison, IDn_a, IDn_b)
    parameters = {
        "winner_idn": winner_idn,
        "loser_idn": loser_idn,
        "reason": comparison["reasoning"],
    }
    print(parameters)
    execute_neo4j_query(query, parameters)
    print(f"Winner: {winner_idx}, Loser: {loser_idx}", comparison)

# -The Losing test----------------------------------------------------------------------------------------

memory = ChatMemoryBuffer.from_defaults(token_limit=6000)
idx_a = 0
idx_b = 1
IDn_a = adverts["IDn"][idx_a]
IDn_b = adverts["IDn"][idx_b]

memory.reset()
advert_prompt = create_advert_prompt(IDn_a, IDn_b)
documents = [
    Document(
        text=adverts["advert"][idx_a], metadata={"IDn": str(adverts["IDn"][idx_a])}
    ),
    Document(
        text=adverts["advert"][idx_b], metadata={"IDn": str(adverts["IDn"][idx_b])}
    ),
]

index = VectorStoreIndex.from_documents(documents, llm=llm)


# Initial comparison between the first two adverts
comparison = compare_adverts(index, advert_prompt)
winner_idx, loser_idx, next_id = get_indeces(comparison, idx_a, idx_b)
winner_idn, loser_idn = get_ids(comparison, IDn_a, IDn_b)
parameters = {
    "winner_idn": winner_idn,
    "loser_idn": loser_idn,
    "reason": comparison["reasoning"],
}
query = """MATCH (loser:Posting), (winner:Posting) WHERE ID(loser)=$loser_idn AND ID(winner)=$winner_idn WITH loser, winner
MERGE (winner)<-[:IS_MORE_SUSPICIOUS {reason:$reason}]-(loser)"""
execute_neo4j_query(query, parameters)
print(comparison["reasoning"])
for i in range(2, len(adverts)):
    IDn_a = adverts["IDn"][next_id]
    IDn_b = adverts["IDn"][loser_idx]
    advert_prompt = create_advert_prompt(IDn_a, IDn_b)
    documents = [
        Document(
            text=adverts["advert"][next_id],
            metadata={"IDn": str(adverts["IDn"][next_id])},
        ),
        Document(
            text=adverts["advert"][loser_idx],
            metadata={"IDn": str(adverts["IDn"][loser_idx])},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    winner_idx, loser_idx, next_id = get_indeces(comparison, winner_idx, next_id)
    winner_idn, loser_idn = get_ids(comparison, IDn_a, IDn_b)
    parameters = {
        "winner_idn": winner_idn,
        "loser_idn": loser_idn,
        "reason": comparison["reasoning"],
    }
    print(parameters)
    execute_neo4j_query(query, parameters)
    print(f"Winner: {winner_idx}, Loser: {loser_idx}", comparison)

# -Loser Reboot----------------------------------------------------------------------------------------
for i in range(2, len(adverts)):
    node_a = str(adverts["IDn"][next_row])
    node_b = str(adverts["IDn"][loser_row])
    advert_a = adverts["advert"][next_row]
    advert_b = adverts["advert"][loser_row]
    advert_prompt = create_advert_prompt(node_a, node_b)
    documents = [
        Document(
            text=advert_a,
            metadata={"IDn": node_a},
        ),
        Document(
            text=advert_b,
            metadata={"IDn": node_b},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    if comparison is None:
        next_id += 1
    else:
        winner_row, loser_row, next_row = get_indeces(comparison, winner_row, next_row)
        winner_node, loser_node = get_ids(comparison, node_a, node_b)
        parameters = {
            "winner_node": winner_node,
            "loser_node": loser_node,
            "reason": comparison["reasoning"],
        }
        print(parameters)
        execute_neo4j_query(query, parameters)
        print(f"Winner row: {winner_row}, loser row: {loser_row}", comparison)


def loser_iterator(adverts, llm, query, winner_row, loser_row, next_row):
    node_a = str(adverts["IDn"][next_row])
    node_b = str(adverts["IDn"][loser_row])
    advert_a = adverts["advert"][next_row]
    advert_b = adverts["advert"][loser_row]
    advert_prompt = create_advert_prompt(node_a, node_b)
    documents = [
        Document(
            text=advert_a,
            metadata={"IDn": node_a},
        ),
        Document(
            text=advert_b,
            metadata={"IDn": node_b},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    winner_row, loser_row, next_row = get_indeces(comparison, winner_row, next_row)
    winner_node, loser_node = get_ids(comparison, node_a, node_b)
    parameters = {
        "winner_node": winner_node,
        "loser_node": loser_node,
        "reason": comparison["reasoning"],
    }
    print(parameters)
    execute_neo4j_query(query, parameters)
    print(f"Winner row: {winner_row}, loser row: {loser_row}", comparison)


# -Random Iterator----------------------------------------------------------------------------------------
