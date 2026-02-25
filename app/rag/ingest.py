"""Ingest sources/*.pdf and sources/*.md into ChromaDB."""

from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL, SOURCES_DIR


def ingest_sources(
    sources_dir: Path = SOURCES_DIR,
    chroma_dir: Path = CHROMA_DIR,
) -> Chroma:
    """Load all source documents, chunk them, and persist to ChromaDB.

    Returns the Chroma vector store instance.
    """
    docs = []

    # Load markdown files
    for md_file in sorted(sources_dir.glob("*.md")):
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs.extend(loader.load())

    # Load PDF files
    for pdf_file in sorted(sources_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_file))
        docs.extend(loader.load())

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)

    # Create embeddings and persist
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(chroma_dir),
    )

    return vectorstore


def load_vectorstore(chroma_dir: Path = CHROMA_DIR) -> Chroma:
    """Load an existing ChromaDB from disk."""
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embeddings,
    )
