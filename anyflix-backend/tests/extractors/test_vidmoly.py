#!/usr/bin/env python3
"""Pytest-based test for Vidmoly extractor."""

import pytest

from lib.extractors.vidmoly_extractor import vidmoly_extractor
from tests.extractor_test_base import SingleURLExtractorTest


class TestVidmolyExtractor:
    """Pytest class for Vidmoly extractor using base test functionality."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for Vidmoly."""
        return "https://vidmoly.net/embed-16jl3rm2nwfj.html"

    @pytest.fixture
    def extractor_test(self, test_url):
        """Return configured extractor test instance."""
        return VidmolyTestImpl(test_url)

    @pytest.mark.asyncio
    async def test_vidmoly_extraction(self, extractor_test):
        """Test Vidmoly video extraction using base test class."""
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
    async def test_vidmoly_invalid_url(self):
        """Test Vidmoly extractor with invalid URL."""
        invalid_url = "https://vidmoly.net/embed-invalid.html"
        sources = await vidmoly_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"

    def test_manual_run(self, extractor_test, capsys):
        """Test manual run functionality."""
        extractor_test.run_tests()
        captured = capsys.readouterr()
        assert "Testing Vidmoly extractor" in captured.out


class VidmolyTestImpl(SingleURLExtractorTest):
    """Implementation of Vidmoly test for pytest."""

    def __init__(self, test_url: str):
        super().__init__(
            extractor_name="Vidmoly",
            extractor_func=vidmoly_extractor,
            test_url=test_url,
        )
