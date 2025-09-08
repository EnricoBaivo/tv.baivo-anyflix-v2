#!/usr/bin/env python3
"""Pytest-based test for FileMoon extractor."""

import pytest

from lib.extractors.filemoon_extractor import filemoon_extractor
from tests.extractor_test_base import SingleURLExtractorTest


class TestFileMoonExtractor:
    """Pytest class for FileMoon extractor using base test functionality."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for FileMoon."""
        return "https://filemoon.to/d/iiwums6tekoj"

    @pytest.fixture
    def extractor_test(self, test_url):
        """Return configured extractor test instance."""
        return FileMoonTestImpl(test_url)

    @pytest.mark.asyncio
    async def test_filemoon_extraction(self, extractor_test):
        """Test FileMoon video extraction using base test class."""
        extractor_func = extractor_test.get_extractor_function()
        test_urls = extractor_test.get_test_urls()

        for url in test_urls:
            sources = await extractor_func(url)

            # Basic assertions
            assert sources is not None, "Sources should not be None"

            if sources:  # If extraction succeeded
                assert len(sources) > 0, "Should have at least one source"

                for source in sources:
                    assert hasattr(source, "url"), "Source should have URL"
                    assert hasattr(source, "quality"), "Source should have quality"
                    assert source.url, "URL should not be empty"
                    assert source.quality, "Quality should not be empty"

    @pytest.mark.asyncio
    async def test_filemoon_invalid_url(self):
        """Test FileMoon extractor with invalid URL."""
        invalid_url = "https://filemoon.to/d/invalid_url"
        sources = await filemoon_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"

    def test_manual_run(self, extractor_test, capsys):
        """Test manual run functionality."""
        extractor_test.run_tests()
        captured = capsys.readouterr()
        assert "Testing FileMoon extractor" in captured.out


class FileMoonTestImpl(SingleURLExtractorTest):
    """Implementation of FileMoon test for pytest."""

    def __init__(self, test_url: str):
        super().__init__(
            extractor_name="FileMoon",
            extractor_func=filemoon_extractor,
            test_url=test_url,
        )
