"""Base classes for extractor tests."""

import asyncio
from typing import Callable


class SingleURLExtractorTest:
    """Base test class for single URL extractors."""

    def __init__(
        self,
        extractor_name: str,
        extractor_func: Callable,
        test_url: str,
    ):
        """Initialize single URL extractor test.

        Args:
            extractor_name: Name of the extractor for display
            extractor_func: The extractor function to test
            test_url: Test URL to use
        """
        self.extractor_name = extractor_name
        self.extractor_func = extractor_func
        self.test_url = test_url

    def get_extractor_function(self) -> Callable:
        """Get the extractor function.

        Returns:
            The extractor function
        """
        return self.extractor_func

    def get_test_urls(self) -> list[str]:
        """Get test URLs as a list.

        Returns:
            List containing the test URL
        """
        return [self.test_url]

    def run_tests(self):
        """Run manual tests for the extractor."""
        print(f"Testing {self.extractor_name} extractor")
        print(f"Test URL: {self.test_url}")

        # Check if the extractor is async
        if asyncio.iscoroutinefunction(self.extractor_func):
            # Run async extractor
            result = asyncio.run(self.extractor_func(self.test_url))
        else:
            # Run sync extractor
            result = self.extractor_func(self.test_url)

        if result:
            print(f"✓ Extraction successful: {len(result)} source(s) found")
            for i, source in enumerate(result, 1):
                print(f"  Source {i}:")
                print(f"    Quality: {source.quality}")
                print(f"    URL: {source.url[:80]}...")
        else:
            print("✗ Extraction failed or returned empty results")


class MultiURLExtractorTest:
    """Base test class for multi-URL extractors."""

    def __init__(
        self,
        extractor_name: str,
        extractor_func: Callable,
        test_urls: list[str],
    ):
        """Initialize multi-URL extractor test.

        Args:
            extractor_name: Name of the extractor for display
            extractor_func: The extractor function to test
            test_urls: List of test URLs to use
        """
        self.extractor_name = extractor_name
        self.extractor_func = extractor_func
        self.test_urls = test_urls

    def get_extractor_function(self) -> Callable:
        """Get the extractor function.

        Returns:
            The extractor function
        """
        return self.extractor_func

    def get_test_urls(self) -> list[str]:
        """Get test URLs.

        Returns:
            List of test URLs
        """
        return self.test_urls

    def run_tests(self):
        """Run manual tests for the extractor."""
        print(f"Testing {self.extractor_name} extraction")
        print(f"Test URLs: {len(self.test_urls)}")

        for i, url in enumerate(self.test_urls, 1):
            print(f"\nTest {i}/{len(self.test_urls)}: {url}")

            # Check if the extractor is async
            if asyncio.iscoroutinefunction(self.extractor_func):
                # Run async extractor
                result = asyncio.run(self.extractor_func(url))
            else:
                # Run sync extractor
                result = self.extractor_func(url)

            if result:
                print(f"  ✓ Extraction successful: {len(result)} source(s) found")
                for j, source in enumerate(result[:3], 1):  # Show first 3 sources
                    print(f"    Source {j}:")
                    print(f"      Quality: {source.quality}")
                    print(f"      URL: {source.url[:60]}...")
                if len(result) > 3:
                    print(f"    ... and {len(result) - 3} more")
            else:
                print("  ✗ Extraction failed or returned empty results")
