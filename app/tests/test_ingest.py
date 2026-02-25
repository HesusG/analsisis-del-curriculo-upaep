"""Tests for RAG ingestion."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from rag.ingest import ingest_sources


class TestIngest:
    def test_loads_markdown_files(self, tmp_path):
        """Verify markdown files are discovered and loaded."""
        src = tmp_path / "sources"
        src.mkdir()
        (src / "test1.md").write_text("# Test\nContent here.", encoding="utf-8")
        (src / "test2.md").write_text("# Test 2\nMore content.", encoding="utf-8")

        chroma_dir = tmp_path / "chroma"

        with patch("rag.ingest.OpenAIEmbeddings") as mock_emb, \
             patch("rag.ingest.Chroma") as mock_chroma:
            mock_emb_instance = MagicMock()
            mock_emb.return_value = mock_emb_instance
            mock_chroma.from_documents.return_value = MagicMock()

            ingest_sources(sources_dir=src, chroma_dir=chroma_dir)

            # Verify from_documents was called with chunks
            call_kwargs = mock_chroma.from_documents.call_args.kwargs
            assert len(call_kwargs["documents"]) > 0
            assert call_kwargs["embedding"] is mock_emb_instance

    def test_empty_sources_dir(self, tmp_path):
        """Empty sources dir should still work (0 docs)."""
        src = tmp_path / "sources"
        src.mkdir()
        chroma_dir = tmp_path / "chroma"

        with patch("rag.ingest.OpenAIEmbeddings") as mock_emb, \
             patch("rag.ingest.Chroma") as mock_chroma:
            mock_emb.return_value = MagicMock()
            mock_chroma.from_documents.return_value = MagicMock()

            ingest_sources(sources_dir=src, chroma_dir=chroma_dir)

            call_kwargs = mock_chroma.from_documents.call_args.kwargs
            assert len(call_kwargs["documents"]) == 0
