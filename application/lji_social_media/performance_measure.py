import pandas as pd
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
import json

llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=64000)
memory = ChatMemoryBuffer.from_defaults(token_limit=64000)
comparison = pd.read_csv("results/comparison.csv")
rename = {
    "advert_y": "text",
    "Rating 1 - 10 (10 is most likely to be HT)": "rating",
    "Reason": "reason",
}
comparison.rename(columns=rename, inplace=True)
adverts = pd.read_csv("results/adverts.csv")
list(comparison)
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
            "You rate adverts on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
            "You are specifically looking for perpetrators who are using employment advertisements to exploit victims. "
        ),
    )


def generate_ratings(chat_engine, data, text_column, prompt) -> list:
    ratings = []
    for i, row in data.iterrows():
        advert = row[text_column]
        memory.reset()
        user_prompt = prompt.format(advert=advert)
        response = chat_engine.chat(user_prompt)
        print(response.response, user_prompt)
        formatted_response = (
            response.response.strip()
        )  # Remove leading/trailing whitespace

        s = json.loads(formatted_response)
        ratings.append(s)
    return ratings


def generate_gpt_ratings(data, text_column, prompt) -> list:
    ratings = []
    for i, row in data.iterrows():
        advert = row[text_column]
        document = Document(text=advert)
        memory.reset()
        index = VectorStoreIndex.from_documents([document], llm=llm)
        chat_engine = index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt=(
                "As a career forensic analyst you have deep insight into crime and criminal activity especially the field of "
                "online human trafficking. "
                "You are careful and precise and can compare adverts in the finest detail."
                "You rate adverts on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
                "You are specifically looking for perpetrators who are using employment advertisements to exploit victims. "
            ),
        )
        response = chat_engine.chat(prompt)
        print(response.response, prompt)
        formatted_response = (
            response.response.strip()
        )  # Remove leading/trailing whitespace

        s = json.loads(formatted_response)
        ratings.append(s)
    return ratings


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

# Compare two adverts with LJI monitor feedback:
prompt = (
    f"Which of  advert text A ```{row_i['text']}```"
    f"or advert B {row_j['text']} is more likely to be either fake, fraudulent or a scam in the business of human trafficking and why?"
)
response = chat_engine.chat(prompt)

# Compare two adverts with LJI monitor feedback AND know signs of fraudulent adverts:
advert = adverts.sample(1).values[0][1]
prompt = (
    f"Assistant, which of  advert text A ```{row_i['text']}```"
    f"or advert B ```{advert}``` is more likely to be either fake, fraudulent or a scam in the business of human trafficking and why?"
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
)

response = chat_engine.chat(prompt)
print(response.response)

#  Rate an advert using LJI monitor feedback:
advert = row_i["text"]
advert = adverts.sample(1).values[0][1]
prompt = (
    f"Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
    f"Please provide you rating on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
    f"Also provide a reason for your rating."
    f"Please provide your response in JSON format and ensure it can be parsed correctly."
    f"Here is an example:"
    f'{{"rating": integer, "reason": "reasoning"}}'
)
memory.reset()
response = chat_engine.chat(prompt)
print(response.response)
formatted_response = response.response.strip()  # Remove leading/trailing whitespace

s = json.loads(formatted_response)

lji_prompt = (
    "Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
    "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
    "Also provide a reason for your rating."
    "Please provide your response in JSON format and ensure it can be parsed correctly."
    "Here is an example:"
    '{{"rating": integer, "reason": "reasoning"}}"'
)

gpt_lji_prompt = (
    "Assistant please provide a rating and a reason for the following advert ```{advert}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
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

gpt_prompt = (
    "Assistant please provide an assessment of the provided text for being a fake, fraudulent or scam in the business of human trafficking together with carefully crafted reason."
    "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to being fake, fraudulent or a scam in the business of human trafficking."
    "Also provide a reason for your rating."
    "Provide your response in JSON format and ensure it can be parsed correctly."
    "If the adverts mention multiple offers, assess them as one."
    "Here is an example:"
    '{{"rating": integer, "reason": "reasoning"}}"'
)
# 1. Rate all adverts from comparisons using the minimum LJI RAG model

ratings = generate_ratings(chat_engine, comparison, "text", lji_prompt)
LJI_RAG_comparison_ratings = pd.DataFrame(ratings)
LJI_RAG_comparison_ratings.rename(
    columns={"rating": "LJI_RAG_rating", "reason": "LJI_RAG_reason"}, inplace=True
)
comparison.join(LJI_RAG_comparison_ratings).to_csv(
    "results/LJI_RAG_comparison_ratings.csv", index=False
)

# 2. Rate all adverts from comparisons using the GPT/LJI RAG model
ratings = generate_ratings(chat_engine, comparison, "text", gpt_lji_prompt)

GPTLJI_RAG_comparison_ratings = pd.DataFrame(ratings)
GPTLJI_RAG_comparison_ratings.rename(
    columns={"rating": "GPTLJI_RAG_rating", "reason": "GPTLJI_RAG_reason"}, inplace=True
)
comparison.join(GPTLJI_RAG_comparison_ratings).to_csv(
    "results/GPTLJI_RAG_comparison_ratings.csv", index=False
)

# 3. Rate all adverts from adverts using the minimum LJI RAG model
ratings = generate_ratings(chat_engine, adverts, "advert", lji_prompt)
LJI_RAG_adverts_ratings = pd.DataFrame(ratings)
LJI_RAG_adverts_ratings.rename(
    columns={"rating": "LJI_RAG_advert_rating", "reason": "LJI_RAG_advert_reason"},
    inplace=True,
)
adverts.join(LJI_RAG_adverts_ratings).to_csv(
    "results/LJI_RAG_adverts_ratings.csv", index=False
)

# 4. Rate all adverts from adverts using the GPTLJI RAG model
ratings = generate_ratings(chat_engine, adverts, "advert", gpt_lji_prompt)

GPTLJI_RAG_adverts_ratings = pd.DataFrame(ratings)
GPTLJI_RAG_adverts_ratings.rename(
    columns={
        "rating": "GPTLJI_RAG_advert_rating",
        "reason": "GPTLJI_RAG_advert_reason",
    },
    inplace=True,
)
adverts.join(GPTLJI_RAG_adverts_ratings).to_csv(
    "results/GPTLJI_RAG_adverts_ratings.csv", index=False
)

# 5. Rate all adverts from adverts using  pure GPT:
ratings = generate_gpt_ratings(data=adverts, text_column="advert", prompt=gpt_prompt)
list(adverts)
GPT_adverts_ratings = pd.DataFrame(ratings)
GPT_adverts_ratings.rename(
    columns={
        "rating": "GPT_advert_rating",
        "reason": "GPT_advert_reason",
    },
    inplace=True,
)
adverts.join(GPT_adverts_ratings).to_csv("results/GPT_adverts_ratings.csv", index=False)
# rmse = np.sqrt(mean_squared_error(y_true, y_pred))

GPTLJI_RAG_adverts_ratings = pd.read_csv("results/GPTLJI_RAG_adverts_ratings.csv")
LJI_RAG_adverts_ratings = pd.read_csv("results/LJI_RAG_adverts_ratings.csv")
GPT_adverts_ratings = pd.read_csv("results/GPT_adverts_ratings.csv")
list(GPTLJI_RAG_adverts_ratings)
list(LJI_RAG_adverts_ratings)
LJI_RAG = LJI_RAG_adverts_ratings["LJI_RAG_advert_rating"].to_list()
GPTLJI_RAG = GPTLJI_RAG_adverts_ratings["GPTLJI_RAG_advert_rating"].to_list()
GPT = GPT_adverts_ratings["GPT_advert_rating"].to_list()


# Visual and quantitative analysis of the ratings
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
import matplotlib.pyplot as plt
import seaborn as sns

# Sample data


# Convert lists to DataFrame
df = pd.DataFrame({"List1": LJI_RAG, "List2": GPTLJI_RAG, "List3": GPT})

# Calculate correlation coefficients
correlations = {
    "Pearson": df.corr(method="pearson"),
    "Spearman": df.corr(method="spearman"),
    "Kendall": df.corr(method="kendall"),
}

print("Correlation Coefficients:")
for method, corr_matrix in correlations.items():
    print(f"\n{method}:\n{corr_matrix}")

# Scatter plots
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.scatter(LJI_RAG, GPTLJI_RAG)
plt.title("List1 vs List2")
plt.xlabel("List1")
plt.ylabel("List2")

plt.subplot(1, 3, 2)
plt.scatter(list1, list3)
plt.title("List1 vs List3")
plt.xlabel("List1")
plt.ylabel("List3")

plt.subplot(1, 3, 3)
plt.scatter(list2, list3)
plt.title("List2 vs List3")
plt.xlabel("List2")
plt.ylabel("List3")

plt.tight_layout()
plt.show()

# Pair plot
sns.pairplot(df)
plt.show()

# import numpy as np
#
# np.
# np.sqrt(mean_squared_error(y_true, y_pred))

#
