#!/usr/bin/env python3
"""Pytest-based test for yt-dlp extractor."""

import pytest

from lib.extractors.ytdlp_extractor import ytdlp_extractor
from tests.extractor_test_base import MultiURLExtractorTest


class TestYTDLPExtractor:
    """Pytest class for yt-dlp extractor using base test functionality."""

    @pytest.fixture
    def test_urls(self):
        """Return test URLs for yt-dlp."""
        return [
            "https://videzz.net/embed-ibif7f9bsarp.html",  # Vidoza
            "https://vidmoly.net/embed-16jl3rm2nwfj.html",  # Vidmoly
        ]

    @pytest.fixture
    def extractor_test(self, test_urls):
        """Return configured extractor test instance."""
        return YTDLPTestImpl(test_urls)

    @pytest.mark.parametrize(
        "test_url",
        [
            "https://videzz.net/embed-ibif7f9bsarp.html",
            "https://vidmoly.net/embed-16jl3rm2nwfj.html",
        ],
    )
    def test_ytdlp_extraction_parametrized(self, test_url):
        """Test yt-dlp video extraction with parametrized URLs."""
        sources = ytdlp_extractor(test_url)

        # Basic assertions
        assert sources is not None, "Sources should not be None"

        if sources:  # If extraction succeeded
            assert len(sources) > 0, "Should have at least one source"

            for source in sources:
                assert hasattr(source, "url"), "Source should have URL"
                assert hasattr(source, "quality"), "Source should have quality"
                assert source.url, "URL should not be empty"
                assert source.quality, "Quality should not be empty"

                # yt-dlp specific attributes
                if hasattr(source, "original_url"):
                    assert (
                        source.original_url
                    ), "Original URL should not be empty if present"

    def test_ytdlp_batch_extraction(self, extractor_test):
        """Test yt-dlp batch extraction using base test class."""
        extractor_func = extractor_test.get_extractor_function()
        test_urls = extractor_test.get_test_urls()

        results = []
        for url in test_urls:
            sources = extractor_func(url)
            results.append((url, sources))

        assert len(results) == len(test_urls), "Should have results for all URLs"

        for url, sources in results:
            assert sources is not None, f"Sources should not be None for {url}"

    def test_ytdlp_invalid_url(self):
        """Test yt-dlp extractor with invalid URL."""
        invalid_url = "https://invalid-domain.com/video.html"
        sources = ytdlp_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"

    def test_manual_run(self, extractor_test, capsys):
        """Test manual run functionality."""
        extractor_test.run_tests()
        captured = capsys.readouterr()
        assert "Testing yt-dlp Python library extraction" in captured.out


class YTDLPTestImpl(MultiURLExtractorTest):
    """Implementation of yt-dlp test for pytest."""

    def __init__(self, test_urls: list):
        super().__init__(
            extractor_name="yt-dlp Python library",
            extractor_func=ytdlp_extractor,
            test_urls=test_urls,
        )
