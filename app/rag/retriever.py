"""Semantic search wrapper over ChromaDB."""

from __future__ import annotations

from langchain_core.vectorstores import VectorStoreRetriever

from config import CHROMA_DIR, RETRIEVER_K
from rag.ingest import load_vectorstore


def get_retriever(chroma_dir=CHROMA_DIR, k: int = RETRIEVER_K) -> VectorStoreRetriever:
    """Return a retriever backed by the persisted ChromaDB."""
    vectorstore = load_vectorstore(chroma_dir)
    return vectorstore.as_retriever(search_kwargs={"k": k})
