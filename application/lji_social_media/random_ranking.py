import pandas as pd
import re
import json
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from libraries.neo4j_lib import execute_neo4j_query
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

llm = OpenAI(temperature=0, model="gpt-4o")
memory = ChatMemoryBuffer.from_defaults(token_limit=64000)

from time import sleep
import random


def try_fix_json(broken_json):
    # Example fix: remove trailing commas before closing brackets or braces
    try:
        fixed_json = re.sub(r",\s*([}\]])", r"\1", broken_json)
        return fixed_json
    except Exception as e:
        print("Failed to fix JSON:", e)
        return None


def winner_loser(node_a, node_b):
    return node_a if random.random() > 0.5 else node_b


def get_adverts():
    query = """MATCH (n:Posting) WHERE (n.text IS NOT NULL) AND NOT (n.text = "") RETURN ID(n) AS IDn, n.post_id, n.post_url AS post_url, n.text AS advert"""
    postings = execute_neo4j_query(query, {})
    return pd.DataFrame(postings)


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


def get_parameters(winner_node, loser_node, comparison):
    return {
        "winner_node": int(winner_node),
        "loser_node": int(loser_node),
        "reason": comparison["reasoning"],
    }


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


adverts = get_adverts()
idns = adverts["IDn"].to_list()
random.shuffle(idns)
advert_prompt = create_advert_prompt()

index_a = 0
index_b = 1
query = """MATCH (loser:Posting), (winner:Posting) WHERE ID(loser)=$loser_node AND ID(winner)=$winner_node WITH loser, winner
MERGE (winner)<-[:IS_MORE_SUSPICIOUS {reason:$reason}]-(loser)"""
for i in range(len(idns) - 2):
    winner_node = idns[index_a]
    loser_node = idns[index_b]
    print("Comparing adverts", index_a, "and", index_b)
    adverta = adverts.loc[adverts.IDn == winner_node, "advert"].values[0]
    print(adverta[:500])
    advertb = adverts.loc[adverts.IDn == loser_node, "advert"].values[0]
    print(advertb[:500])
    documents = [
        Document(
            text=adverta,
            metadata={"advert": "advert_a"},
        ),
        Document(
            text=advertb,
            metadata={"advert": "advert_b"},
        ),
    ]
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    comparison = compare_adverts(index, advert_prompt)
    if comparison is not None:
        if comparison["most suspect"] == "advert_b":
            print("Swapping nodes")
            loser_node, winner_node, index_a = (
                winner_node,
                loser_node,
                index_b,
            )  # Swap nodes
        parameters = get_parameters(winner_node, loser_node, comparison)  # Swap nodes
        execute_neo4j_query(query, parameters)
        index_b = max(index_a, index_b) + 1
        if comparison["most suspect"] == "neither":
            print("Neither advert was suspect.")
            parameters = get_parameters(winner_node, loser_node, comparison)
            print(parameters)
            execute_neo4j_query(query, parameters)
            parameters = get_parameters(loser_node, winner_node, comparison)
            print(parameters)
            execute_neo4j_query(query, parameters)
    sleep(3)
