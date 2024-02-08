import streamlit as st
from llama_index.retrievers import AutoMergingRetriever
from llama_index.indices.postprocessor import SentenceTransformerRerank
from llama_index.query_engine import RetrieverQueryEngine
from llama_index import VectorStoreIndex, StorageContext
from llama_index import ServiceContext
from llama_index import load_index_from_storage
import os
from llama_index.node_parser import HierarchicalNodeParser, get_leaf_nodes


def load_automerging_index(
    llm, embed_model="local:BAAI/bge-small-en-v1.5", save_dir="merging_index"
):
    merging_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
    )
    automerging_index = load_index_from_storage(
        StorageContext.from_defaults(persist_dir=save_dir),
        service_context=merging_context,
    )
    return automerging_index


@st.cache(allow_output_mutation=True)
def get_automerging_query_engine(
    automerging_index,
    similarity_top_k=12,
    rerank_top_n=6,
):
    base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        base_retriever, automerging_index.storage_context, verbose=True
    )
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, node_postprocessors=[rerank]
    )
    return auto_merging_engine


def build_automerging_index(documents, llm, embed_model, save_dir, chunk_sizes):
    """Builds an auto-merging index from documents."""

    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)
    merging_context = ServiceContext.from_defaults(llm=llm, embed_model=embed_model)
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    if not os.path.exists(save_dir):
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context, service_context=merging_context
        )
        automerging_index.storage_context.persist(persist_dir=save_dir)
    else:
        automerging_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir),
            service_context=merging_context,
        )

    return automerging_index
