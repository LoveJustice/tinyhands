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
    if "comparison_data" not in st.session_state:
        comparison = pd.read_csv("results/comparison.csv")
        rename = {
            "advert_y": "text",
            "Rating 1 - 10 (10 is most likely to be HT)": "rating",
            "Reason": "reason",
        }
        comparison.rename(columns=rename, inplace=True)

        st.dataframe(comparison)
        documents = create_documents(comparison)
        memory.reset()
        index = VectorStoreIndex.from_documents(documents, llm=llm)
        st.session_state.chat_engine = create_chat_engine(index)


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
    st.write("This platform helps to rank and rate suspicious recruitment adverts.")
    # st.text_input("Enter the text of an advert here...", key="advert_text")
    st.text_area(
        "Enter the text of an advert here...",
        key="advert_text",
        height=200,
        max_chars=5000,
    )
    st.sidebar.radio(
        "A ranking/rating method", ["LJI RAG", "LJI-GPT RAG", "GPT"], key="method"
    )
    init_session()
    with st.expander("Click to reveal the original LJI sample adverts"):
        st.dataframe(st.session_state.comparison_data[["text", "rating", "reason"]])

    if st.button("Submit"):
        st.write("The advert has been submitted.")
        prompt = get_prompt()
        if st.session_state.method in ["LJI RAG", "LJI-GPT RAG"]:
            response = st.session_state.chat_engine.chat(prompt)
            formatted_response = (
                response.response.strip()
            )  # Remove leading/trailing whitespace

            s = json.loads(formatted_response)
            st.write(f'The advert achieves a rating of {s["rating"]}')
            st.markdown(s["reason"])
        if st.session_state.method == "GPT":
            document = Document(text=st.session_state["advert_text"])
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

            formatted_response = (
                response.response.strip()
            )  # Remove leading/trailing whitespace

            s = json.loads(formatted_response)
            st.write(f'The advert achieves a rating of {s["rating"]}')
            st.markdown(s["reason"])


if __name__ == "__main__":
    main()
