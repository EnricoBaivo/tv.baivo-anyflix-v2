#!/usr/bin/env python3
"""Base test class for extractor testing."""

import asyncio
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Union


class ExtractorTestBase(ABC):
    """Base class for testing video extractors."""

    def __init__(self, extractor_name: str):
        """Initialize the test base.

        Args:
            extractor_name: Name of the extractor being tested
        """
        self.extractor_name = extractor_name
        self.test_urls = []

    @abstractmethod
    def get_extractor_function(self) -> Callable:
        """Return the extractor function to test.

        Returns:
            The extractor function (sync or async)
        """
        pass

    @abstractmethod
    def get_test_urls(self) -> List[str]:
        """Return list of test URLs for this extractor.

        Returns:
            List of test URLs
        """
        pass

    def print_header(self, url: str) -> None:
        """Print test header."""
        print(f"Testing {self.extractor_name} extractor with URL: {url}")
        print("-" * 60)

    def print_success(self, sources: List[Any]) -> None:
        """Print success message and source details."""
        print(f"✅ Found {len(sources)} video source(s):")
        for i, source in enumerate(sources, 1):
            print(f"  Source {i}:")
            print(f"    URL: {source.url}")
            print(f"    Quality: {source.quality}")

            # Handle optional attributes that may not exist on all source types
            if hasattr(source, "original_url") and source.original_url:
                print(f"    Original URL: {source.original_url}")

            if hasattr(source, "headers") and source.headers:
                print(f"    Headers: {source.headers}")

            if hasattr(source, "subtitles") and source.subtitles:
                subtitle_count = (
                    len(source.subtitles)
                    if isinstance(source.subtitles, list)
                    else "available"
                )
                print(f"    Subtitles: {subtitle_count}")

            if hasattr(source, "audios") and source.audios:
                audio_count = (
                    len(source.audios)
                    if isinstance(source.audios, list)
                    else "available"
                )
                print(f"    Audio tracks: {audio_count}")

            print()

    def print_failure(self) -> None:
        """Print failure message."""
        print("❌ No video sources found")

    def print_error(self, error: Exception) -> None:
        """Print error message and traceback."""
        print(f"❌ Error occurred: {error}")
        traceback.print_exc()

    async def test_async_extractor(self, url: str, extractor_func: Callable) -> None:
        """Test an async extractor function."""
        self.print_header(url)

        try:
            sources = await extractor_func(url)

            if sources:
                self.print_success(sources)
            else:
                self.print_failure()

        except Exception as e:
            self.print_error(e)

    def test_sync_extractor(self, url: str, extractor_func: Callable) -> None:
        """Test a sync extractor function."""
        self.print_header(url)

        try:
            sources = extractor_func(url)

            if sources:
                self.print_success(sources)
            else:
                self.print_failure()

        except Exception as e:
            self.print_error(e)

    async def run_async_tests(self) -> None:
        """Run async tests for all URLs."""
        extractor_func = self.get_extractor_function()
        test_urls = self.get_test_urls()

        for url in test_urls:
            await self.test_async_extractor(url, extractor_func)
            print()  # Add spacing between tests

    def run_sync_tests(self) -> None:
        """Run sync tests for all URLs."""
        extractor_func = self.get_extractor_function()
        test_urls = self.get_test_urls()

        for url in test_urls:
            self.test_sync_extractor(url, extractor_func)
            print()  # Add spacing between tests

    def run_tests(self) -> None:
        """Run tests (auto-detects async vs sync)."""
        extractor_func = self.get_extractor_function()

        # Check if extractor function is async
        if asyncio.iscoroutinefunction(extractor_func):
            asyncio.run(self.run_async_tests())
        else:
            self.run_sync_tests()


class MultiURLExtractorTest(ExtractorTestBase):
    """Test class for extractors that support multiple URLs."""

    def __init__(
        self, extractor_name: str, extractor_func: Callable, test_urls: List[str]
    ):
        """Initialize multi-URL test.

        Args:
            extractor_name: Name of the extractor
            extractor_func: The extractor function
            test_urls: List of URLs to test
        """
        super().__init__(extractor_name)
        self._extractor_func = extractor_func
        self._test_urls = test_urls

    def get_extractor_function(self) -> Callable:
        """Return the extractor function."""
        return self._extractor_func

    def get_test_urls(self) -> List[str]:
        """Return the test URLs."""
        return self._test_urls

    def run_tests(self) -> None:
        """Run tests with header and footer."""
        print(f"Testing {self.extractor_name} extraction")
        print("=" * 60)

        super().run_tests()

        print("=" * 60)
        print(f"{self.extractor_name} testing completed")


class SingleURLExtractorTest(ExtractorTestBase):
    """Test class for extractors that test a single URL."""

    def __init__(self, extractor_name: str, extractor_func: Callable, test_url: str):
        """Initialize single-URL test.

        Args:
            extractor_name: Name of the extractor
            extractor_func: The extractor function
            test_url: URL to test
        """
        super().__init__(extractor_name)
        self._extractor_func = extractor_func
        self._test_url = test_url

    def get_extractor_function(self) -> Callable:
        """Return the extractor function."""
        return self._extractor_func

    def get_test_urls(self) -> List[str]:
        """Return the test URL as a list."""
        return [self._test_url]


