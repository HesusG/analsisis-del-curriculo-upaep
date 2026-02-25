"""One-time local script: ingest sources into ChromaDB Cloud.

Usage:
    cd docker-deploy/scripts
    python ingest_to_cloud.py ../../sources

Reads API keys from ../../simulation/.env or environment variables.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_env():
    """Load .env from simulation/ if available."""
    try:
        from dotenv import load_dotenv

        env_path = Path(__file__).resolve().parent.parent.parent / "simulation" / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded env from {env_path}")
    except ImportError:
        pass


def load_documents(sources_dir: Path) -> list:
    """Load all .md and .pdf files from the sources directory."""
    docs = []

    for md_file in sorted(sources_dir.glob("*.md")):
        print(f"  Loading {md_file.name}")
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs.extend(loader.load())

    for pdf_file in sorted(sources_dir.glob("*.pdf")):
        print(f"  Loading {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        docs.extend(loader.load())

    return docs


def main():
    if len(sys.argv) < 2:
        print("Usage: python ingest_to_cloud.py <sources_directory>")
        sys.exit(1)

    sources_dir = Path(sys.argv[1]).resolve()
    if not sources_dir.is_dir():
        print(f"Error: {sources_dir} is not a directory")
        sys.exit(1)

    load_env()

    # Read config from env
    api_key = os.environ.get("CHROMA_API_KEY", "")
    tenant = os.environ.get("CHROMA_TENANT", "")
    database = os.environ.get("CHROMA_DATABASE", "")
    collection_name = os.getenv("CHROMA_COLLECTION", "curriculo-upaep")
    embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    if not all([api_key, tenant, database]):
        print("Error: CHROMA_API_KEY, CHROMA_TENANT, and CHROMA_DATABASE must be set")
        sys.exit(1)

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY must be set")
        sys.exit(1)

    # 1. Load documents
    print(f"\nLoading documents from {sources_dir}...")
    docs = load_documents(sources_dir)
    print(f"  Loaded {len(docs)} document chunks")

    if not docs:
        print("No documents found. Exiting.")
        sys.exit(1)

    # 2. Split into chunks
    print("\nSplitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)
    print(f"  Created {len(chunks)} chunks")

    # 3. Connect to ChromaDB Cloud
    print("\nConnecting to ChromaDB Cloud...")
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database=database,
    )

    # 4. Delete existing collection for idempotent re-ingestion
    try:
        client.delete_collection(collection_name)
        print(f"  Deleted existing collection '{collection_name}'")
    except Exception:
        print(f"  Collection '{collection_name}' does not exist yet")

    # 5. Embed and push
    print(f"\nEmbedding and pushing {len(chunks)} chunks...")
    embedding_function = OpenAIEmbeddings(model=embedding_model)

    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        client=client,
        collection_name=collection_name,
    )

    print(f"\nDone! {len(chunks)} chunks ingested into '{collection_name}'.")


if __name__ == "__main__":
    main()
