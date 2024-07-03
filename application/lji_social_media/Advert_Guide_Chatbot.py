import streamlit as st
import pandas as pd
import pandas as pd
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import ChatMemoryBuffer
import json


llm = OpenAI(temperature=0, model="gpt-4o", max_tokens=128000)

memory = ChatMemoryBuffer.from_defaults(token_limit=64000)

st.set_page_config(
    page_title="Welcome",
    page_icon="👋",
)


def create_cv_documents(data):
    comparison = pd.read_csv("results/comparison.csv")
    rename = {
        "advert_y": "text",
        "Rating 1 - 10 (10 is most likely to be HT)": "rating",
        "Reason": "reason",
    }
    comparison.rename(columns=rename, inplace=True)


def create_documents(data) -> list:
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


def init_session():
    if "features" not in st.session_state:
        st.session_state["features"] = [
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
    if "comparison_data" not in st.session_state:
        st.session_state["comparison_data"] = pd.read_csv(
            "results/advert_comparison_cleaned.csv"
        ).fillna(0)


def get_prompt():
    prompt = ""
    if st.session_state.method == "LJI-GPT RAG":
        prompt = (
            f"Assistant please provide a rating and a reason for the following advert ```{st.session_state['advert_text']}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
            "Please provide you rating on an integer scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
            "Also provide a reason for your rating.  Please make your reason a bulleted list formatted in markdown."
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
    if st.session_state.method == "LJI RAG":
        prompt = (
            f"Assistant please provide a rating and a reason for the following advert ```{st.session_state['advert_text']}``` for being fake, fraudulent or a scam in the business of human trafficking and why?"
            "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to be used in human trafficking."
            "Also provide a reason for your rating and make it a bulleted list, formatted in markdown."
            "Please provide your response in JSON format and ensure it can be parsed correctly."
            "Here is an example:"
            '{"rating": integer, "reason": "reasoning"}"'
        )

    if st.session_state.method == "GPT":
        prompt = (
            "Assistant please provide an assessment of the provided text for being a fake, fraudulent or scam in the business of human trafficking together with carefully crafted reason."
            "Please provide you rating on a scale of 1 to 10, with 10 being the most likely to being fake, fraudulent or a scam in the business of human trafficking."
            "Also provide a reason for your rating."
            "Provide your reason in a bulleted list, formatted in markdown."
            "Provide your response in JSON format and ensure it can be parsed correctly."
            "If the adverts mention multiple offers, assess them as one."
            "Here is an example:"
            '{"rating": integer, "reason": "reasoning"}"'
        )
    return prompt


def main():
    init_session()
    st.markdown(
        "This platform helps to compare and evaluate ML models for the purpose of rating online adverts "
        "The different models are listed alongside.  Each one uses the same set of pre-labelled data."
        "This data is found here in a Google sheet here."
        "**👈 Select a model from the sidebar** to explore some outcomes"
    )
    st.sidebar.success("Select a demo above.")


if __name__ == "__main__":
    main()
