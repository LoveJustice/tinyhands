import openai
import streamlit as st
import pandas as pd
from pathlib import Path
import json
import pandas as pd

openai.api_key = st.secrets["openai"]["OPENAI_API_KEY"]
models = openai.Model.list()
for model in models["data"]:
    print(model["id"])
sheet_records = pd.read_csv(Path("results/sheet_records.csv"))
sheet_records["div_text"] = sheet_records["div_text"].fillna("")
(
    len(sheet_records["div_text"].fillna("")),
    len(sheet_records["div_text"].fillna("").unique()),
)
div_texts = sheet_records["div_text"].fillna("").unique()
combined_string = " ".join(div_texts)

filename = "results/results.json"
if Path(filename).exists():
    with open(filename, "r") as f:
        data = json.load(f)
else:
    data = {}
len(data["1"]["posts"]["1"]["div_p_texts"][4])
data["1"]["posts"]["1"]["div_p_texts"][4][0]


def get_completion(prompt, model="gpt-3.5-turbo", temperature=0):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model, messages=messages, temperature=temperature
    )
    return response.choices[0].message["content"]


prompt = f"""Please extract the most pertinent and detailed information from this text between the ``` delimiters in the format of a json object, \
and also other detail such detail as the name of the poster and the names of
any other people mentioned in the text.  Please also include the date and time of the post, and the name of the group \
in which the post was made, \
post url, if available, the names of any images or videos that are included, also include the names of any emojis found
and any reactions as well as the names of people commenting and their corresponding text.  \
Please also include the names and detail of any shares that are included:```{combined_string}```"""

result = get_completion(prompt, model="gpt-3.5-turbo-16k", temperature=0)

print(result)
