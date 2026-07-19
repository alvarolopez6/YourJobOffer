import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from backend.utils.pdf_extractor import PdfExtractor


class TestPdfExtractor:

    def test_extract_text_from_pdf(self):
        mock_reader = MagicMock()
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Hello World"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Second Page"
        mock_reader.pages = [mock_page1, mock_page2]

        with patch("backend.utils.pdf_extractor.PdfReader", return_value=mock_reader):
            result = PdfExtractor.extract("/fake/path.pdf")

        assert result == "Hello World\nSecond Page"

    def test_extract_single_page(self):
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Single page content"
        mock_reader.pages = [mock_page]

        with patch("backend.utils.pdf_extractor.PdfReader", return_value=mock_reader):
            result = PdfExtractor.extract("/fake/path.pdf")

        assert result == "Single page content"

    def test_extract_empty_pdf(self):
        mock_reader = MagicMock()
        mock_reader.pages = []

        with patch("backend.utils.pdf_extractor.PdfReader", return_value=mock_reader):
            result = PdfExtractor.extract("/fake/path.pdf")

        assert result == ""
