"""One-shot script to delete and recreate the ChromaDB collection.

Usage:
    CHROMA_API_KEY=... CHROMA_TENANT=... CHROMA_DATABASE=... python scripts/clear_chroma.py
"""

import os
import sys

import chromadb
from chromadb.config import Settings


def main():
    api_key = os.environ.get("CHROMA_API_KEY")
    tenant = os.environ.get("CHROMA_TENANT")
    database = os.environ.get("CHROMA_DATABASE")
    collection = os.environ.get("CHROMA_COLLECTION", "curriculo-upaep")

    if not all([api_key, tenant, database]):
        print("Error: Set CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE env vars.")
        sys.exit(1)

    client = chromadb.HttpClient(
        host="api.trychroma.com",
        port=443,
        ssl=True,
        headers={"x-chroma-token": api_key},
        tenant=tenant,
        database=database,
        settings=Settings(),
    )

    try:
        client.delete_collection(collection)
        print(f"Collection '{collection}' deleted. Will be recreated on first PDF upload.")
    except Exception as e:
        print(f"Error deleting collection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
