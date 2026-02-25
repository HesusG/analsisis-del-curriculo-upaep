"""Tests for PDF text extraction."""

from unittest.mock import MagicMock, patch

from evaluation.pdf_extract import extract_text


def test_extract_text_joins_pages():
    """Verify pages are joined with double newline."""
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 content"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 content"

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page1, mock_page2]

    with patch("evaluation.pdf_extract.PdfReader", return_value=mock_reader):
        result = extract_text("dummy.pdf")

    assert result == "Page 1 content\n\nPage 2 content"


def test_extract_text_handles_none_pages():
    """Pages returning None should be treated as empty strings."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None

    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]

    with patch("evaluation.pdf_extract.PdfReader", return_value=mock_reader):
        result = extract_text("dummy.pdf")

    assert result == ""
