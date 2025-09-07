#!/usr/bin/env python3
"""Pytest-based test for VOE extractor."""

import pytest

from lib.extractors.voe_extractor import voe_extractor
from tests.extractor_test_base import SingleURLExtractorTest


class TestVOEExtractor:
    """Pytest class for VOE extractor using base test functionality."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for VOE."""
        return "https://voe.sx/e/nrn8djmpn2mm"

    @pytest.fixture
    def extractor_test(self, test_url):
        """Return configured extractor test instance."""
        return VOETestImpl(test_url)

    @pytest.mark.asyncio
    async def test_voe_extraction(self, extractor_test):
        """Test VOE video extraction using base test class."""
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
    async def test_voe_invalid_url(self):
        """Test VOE extractor with invalid URL."""
        invalid_url = "https://jilliandescribecompany.com/e/invalid"
        sources = await voe_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"

    def test_manual_run(self, extractor_test, capsys):
        """Test manual run functionality."""
        extractor_test.run_tests()
        captured = capsys.readouterr()
        assert "Testing VOE extractor" in captured.out


class VOETestImpl(SingleURLExtractorTest):
    """Implementation of VOE test for pytest."""

    def __init__(self, test_url: str):
        super().__init__(
            extractor_name="VOE",
            extractor_func=voe_extractor,
            test_url=test_url,
        )
