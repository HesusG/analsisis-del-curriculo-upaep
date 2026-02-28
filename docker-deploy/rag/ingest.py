"""Ingest a user-uploaded PDF into ChromaDB Cloud for RAG retrieval."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHROMA_API_KEY,
    CHROMA_COLLECTION,
    CHROMA_DATABASE,
    CHROMA_TENANT,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
)

logger = logging.getLogger(__name__)


@dataclass
class IngestResult:
    success: bool = False
    chunks_added: int = 0
    skipped_duplicate: bool = False
    error: str | None = None


def compute_fingerprint(pdf_path: str | Path) -> str:
    """SHA-256 of the raw PDF bytes — same content always gives same hash."""
    h = hashlib.sha256()
    with open(pdf_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _has_credentials() -> bool:
    return bool(CHROMA_API_KEY and CHROMA_TENANT and CHROMA_DATABASE)


def _document_exists(collection, fingerprint: str) -> bool:
    """Check if a document with this fingerprint is already in the collection."""
    results = collection.get(
        where={"doc_fingerprint": fingerprint},
        limit=1,
        include=[],
    )
    return len(results["ids"]) > 0


def ingest_pdf(pdf_path: str | Path) -> IngestResult:
    """Chunk, embed, and push a PDF into ChromaDB Cloud.

    This is ADDITIVE — existing documents in the collection are preserved.
    Duplicate PDFs (same SHA-256) are skipped.
    """
    if not _has_credentials():
        return IngestResult(error="ChromaDB credentials not configured")

    try:
        fingerprint = compute_fingerprint(pdf_path)

        client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
        )

        # Get or create the raw chromadb collection for dedup check
        raw_collection = client.get_or_create_collection(CHROMA_COLLECTION)
        if _document_exists(raw_collection, fingerprint):
            return IngestResult(success=True, skipped_duplicate=True)

        # Load and split
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(pages)

        if not chunks:
            return IngestResult(error="PDF produced no text chunks")

        # Enrich metadata
        source_name = Path(pdf_path).name
        for doc in chunks:
            doc.metadata["doc_fingerprint"] = fingerprint
            doc.metadata["source"] = source_name
            doc.metadata["doc_type"] = "user_upload"

        # Embed and push (additive)
        embedding_fn = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(
            client=client,
            collection_name=CHROMA_COLLECTION,
            embedding_function=embedding_fn,
        )
        vectorstore.add_documents(chunks)

        logger.info("Ingested %d chunks from %s", len(chunks), source_name)
        return IngestResult(success=True, chunks_added=len(chunks))

    except Exception as e:
        logger.exception("Ingestion failed for %s", pdf_path)
        return IngestResult(error=str(e))
