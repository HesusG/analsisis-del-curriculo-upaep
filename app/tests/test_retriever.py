"""Tests for RAG retriever."""

from unittest.mock import MagicMock, patch


class TestRetriever:
    def test_get_retriever_returns_retriever(self, tmp_path):
        """Verify retriever wraps ChromaDB with correct k."""
        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever

        with patch("rag.retriever.load_vectorstore", return_value=mock_vectorstore):
            from rag.retriever import get_retriever
            result = get_retriever(chroma_dir=tmp_path, k=3)

        mock_vectorstore.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        assert result is mock_retriever
