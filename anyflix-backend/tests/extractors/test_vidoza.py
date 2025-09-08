#!/usr/bin/env python3
"""Pytest-based test for Vidoza extractor."""

import pytest

from lib.extractors.vidoza_extractor import vidoza_extractor
from tests.extractor_test_base import SingleURLExtractorTest


class TestVidozaExtractor:
    """Pytest class for Vidoza extractor using base test functionality."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for Vidoza."""
        return "https://videzz.net/embed-ibif7f9bsarp.html"

    @pytest.fixture
    def extractor_test(self, test_url):
        """Return configured extractor test instance."""
        return VidozaTestImpl(test_url)

    @pytest.mark.asyncio
    async def test_vidoza_extraction(self, extractor_test):
        """Test Vidoza video extraction using base test class."""
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

                    # Vidoza specific attributes
                    if hasattr(source, "original_url"):
                        assert (
                            source.original_url
                        ), "Original URL should not be empty if present"

    @pytest.mark.asyncio
    async def test_vidoza_invalid_url(self):
        """Test Vidoza extractor with invalid URL."""
        invalid_url = "https://videzz.net/embed-invalid.html"
        sources = await vidoza_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"

    def test_manual_run(self, extractor_test, capsys):
        """Test manual run functionality."""
        extractor_test.run_tests()
        captured = capsys.readouterr()
        assert "Testing Vidoza extractor" in captured.out


class VidozaTestImpl(SingleURLExtractorTest):
    """Implementation of Vidoza test for pytest."""

    def __init__(self, test_url: str):
        super().__init__(
            extractor_name="Vidoza",
            extractor_func=vidoza_extractor,
            test_url=test_url,
        )
