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

# import QueryBundle


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


# define custom retriever


def init_session():
    if "query_engine" not in st.session_state:
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

        st.session_state["query_engine"] = ToolRetrieverRouterQueryEngine(
            obj_index.as_retriever()
        )
    else:
        st.write("the query engine has been built successfully!")


dropdown_models = ["gpt-3.5-turbo", "gpt-4o"]


def main():
    init_session()
    st.sidebar.radio("AI vendor", ["OpenAI", "Anthropic"], key="vendor")
    if st.session_state["vendor"] == "OpenAI":
        dropdown_models = ["gpt-3.5-turbo", "gpt-4o"]
        model = st.sidebar.selectbox(
            "Select OpenAI model here", dropdown_models, key="selected_link"
        )
        Settings.llm = OpenAI(model=model, temperature=0.1)
    if st.session_state["vendor"] == "Anthropic":
        dropdown_models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
        model = st.sidebar.selectbox(
            "Select OpenAI model here", dropdown_models, key="selected_link"
        )

        Settings.llm = Anthropic(model=model, temperature=0.1)

    st.markdown(
        "On this page an ADVERT can be give a MONITOR RATING using a RAG approsch and the advert_guide.pdf."
        "Using another BUTTON the standardized observations are extracted also using the guidelines from the same pdf."
    )
    # st.sidebar.success("Select a demo above.")
    st.text_area(
        "Please place your advert here...",
        key="advert_text",
        height=200,
        max_chars=5000,
    )
    if "query_engine" in st.session_state:
        if st.button("Get Monitor Rating"):
            response = st.session_state["query_engine"].query(
                f"What monitor rating will {st.session_state['advert_text']} most likely receive?"
            )
            st.write(response.response)

        if st.button("Get Standardized Observations"):
            response = st.session_state["query_engine"].query(
                f"As a sessoned anti-human trafficking officer you stick to making observations that are strictly "
                f"from the list as provided in the advert_guide.  "
                f"Which standardized observations can you make for advert {st.session_state['advert_text']}?  "
                f"Please provide your succint list in a json format."
            )
            st.write(response.response)


if __name__ == "__main__":
    main()
