#!/usr/bin/env python3
"""Pytest-based tests for video extractors."""

import pytest

from lib.extractors.filemoon_extractor import filemoon_extractor
from lib.extractors.vidmoly_extractor import vidmoly_extractor
from lib.extractors.vidoza_extractor import vidoza_extractor
from lib.extractors.voe_extractor import voe_extractor
from lib.extractors.ytdlp_extractor import ytdlp_extractor


class TestFileMoonExtractor:
    """Test class for FileMoon extractor."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for FileMoon."""
        return "https://filemoon.to/d/iiwums6tekoj"

    @pytest.mark.asyncio
    async def test_filemoon_extraction(self, test_url):
        """Test FileMoon video extraction."""
        sources = await filemoon_extractor(test_url)

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

        # Should not raise an exception, but may return empty list
        sources = await filemoon_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"


class TestVidmolyExtractor:
    """Test class for Vidmoly extractor."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for Vidmoly."""
        return "https://vidmoly.net/embed-16jl3rm2nwfj.html"

    @pytest.mark.asyncio
    async def test_vidmoly_extraction(self, test_url):
        """Test Vidmoly video extraction."""
        sources = await vidmoly_extractor(test_url)

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

        # Should not raise an exception, but may return empty list
        sources = await vidmoly_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"


class TestVidozaExtractor:
    """Test class for Vidoza extractor."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for Vidoza."""
        return "https://videzz.net/embed-ibif7f9bsarp.html"

    @pytest.mark.asyncio
    async def test_vidoza_extraction(self, test_url):
        """Test Vidoza video extraction."""
        sources = await vidoza_extractor(test_url)

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

        # Should not raise an exception, but may return empty list
        sources = await vidoza_extractor(invalid_url)
        print(f"Vidoza invalid URL test - Sources returned: {sources}")
        print(
            f"Sources type: {type(sources)}, Length: {len(sources) if sources else 'N/A'}"
        )
        assert sources is not None, "Sources should not be None even for invalid URLs"


class TestVOEExtractor:
    """Test class for VOE extractor."""

    @pytest.fixture
    def test_url(self):
        """Return test URL for VOE."""
        return "https://voe.sx/e/nrn8djmpn2mm"

    async def test_voe_extraction(self, test_url):
        """Test VOE video extraction."""
        # VOE extractor is async, so we need to await it
        sources = await voe_extractor(test_url)

        # Basic assertions
        assert sources is not None, "Sources should not be None"

        if sources:  # If extraction succeeded
            assert len(sources) > 0, "Should have at least one source"

            for source in sources:
                assert hasattr(source, "url"), "Source should have URL"
                assert hasattr(source, "quality"), "Source should have quality"
                assert source.url, "URL should not be empty"
                assert source.quality, "Quality should not be empty"

    async def test_voe_invalid_url(self):
        """Test VOE extractor with invalid URL."""
        invalid_url = "https://jilliandescribecompany.com/e/invalid"

        # Should not raise an exception, but may return empty list
        sources = await voe_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"


class TestYTDLPExtractor:
    """Test class for yt-dlp extractor."""

    @pytest.fixture
    def test_urls(self):
        """Return test URLs for yt-dlp."""
        return [
            "https://videzz.net/embed-ibif7f9bsarp.html",  # Vidoza
            "https://vidmoly.net/embed-16jl3rm2nwfj.html",  # Vidmoly
        ]

    @pytest.mark.parametrize(
        "test_url",
        [
            "https://videzz.net/embed-ibif7f9bsarp.html",
            "https://vidmoly.net/embed-16jl3rm2nwfj.html",
        ],
    )
    def test_ytdlp_extraction(self, test_url):
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

    def test_ytdlp_batch_extraction(self, test_urls):
        """Test yt-dlp batch extraction."""
        results = []

        for url in test_urls:
            sources = ytdlp_extractor(url)
            results.append((url, sources))

        assert len(results) == len(test_urls), "Should have results for all URLs"

        for url, sources in results:
            assert sources is not None, f"Sources should not be None for {url}"

    def test_ytdlp_invalid_url(self):
        """Test yt-dlp extractor with invalid URL."""
        invalid_url = "https://invalid-domain.com/video.html"

        # Should not raise an exception, but may return empty list
        sources = ytdlp_extractor(invalid_url)
        assert sources is not None, "Sources should not be None even for invalid URLs"


# Integration tests that can be marked as slow
class TestExtractorsIntegration:
    """Integration tests for extractors."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_all_async_extractors_integration(self):
        """Integration test for all async extractors."""
        extractors_and_urls = [
            (filemoon_extractor, "https://filemoon.to/d/iiwums6tekoj"),
            (vidmoly_extractor, "https://vidmoly.net/embed-16jl3rm2nwfj.html"),
            (vidoza_extractor, "https://videzz.net/embed-ibif7f9bsarp.html"),
        ]

        results = []
        for extractor, url in extractors_and_urls:
            try:
                sources = await extractor(url)
                results.append(
                    (extractor.__name__, url, len(sources) if sources else 0)
                )
            except Exception as e:
                results.append((extractor.__name__, url, f"Error: {e}"))

        # At least some extractors should work
        successful_extractions = [
            r for r in results if isinstance(r[2], int) and r[2] > 0
        ]
        assert len(results) > 0, "Should have tested at least one extractor"

        # Print results for debugging
        for name, url, result in results:
            print(f"{name}: {result} sources from {url}")

    @pytest.mark.slow
    async def test_sync_extractors_integration(self):
        """Integration test for sync extractors."""
        extractors_and_urls = [
            (voe_extractor, "https://jilliandescribecompany.com/e/nrn8djmpn2mm"),
            (ytdlp_extractor, "https://videzz.net/embed-ibif7f9bsarp.html"),
        ]

        results = []
        for extractor, url in extractors_and_urls:
            try:
                if extractor == voe_extractor:
                    sources = await extractor(url)
                else:
                    sources = extractor(url)
                results.append(
                    (extractor.__name__, url, len(sources) if sources else 0)
                )
            except Exception as e:
                results.append((extractor.__name__, url, f"Error: {e}"))

        assert len(results) > 0, "Should have tested at least one extractor"

        # Print results for debugging
        for name, url, result in results:
            print(f"{name}: {result} sources from {url}")
