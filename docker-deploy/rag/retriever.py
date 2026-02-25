"""Semantic search wrapper over ChromaDB Cloud."""

from __future__ import annotations

import chromadb
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings

from config import (
    CHROMA_API_KEY,
    CHROMA_COLLECTION,
    CHROMA_DATABASE,
    CHROMA_TENANT,
    EMBEDDING_MODEL,
    RETRIEVER_K,
)


def get_retriever(k: int = RETRIEVER_K) -> VectorStoreRetriever:
    """Return a retriever backed by ChromaDB Cloud."""
    client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )

    embedding_function = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vectorstore = Chroma(
        client=client,
        collection_name=CHROMA_COLLECTION,
        embedding_function=embedding_function,
    )

    return vectorstore.as_retriever(search_kwargs={"k": k})
