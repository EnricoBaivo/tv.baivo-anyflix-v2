"""Helper functions similar to JavaScript utilities."""

import asyncio
import random
import re
import string
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def clean_html_string(input_str: str) -> str:
    """Clean HTML string by replacing entities and tags.

    Args:
        input_str: Input string to clean

    Returns:
        Cleaned string
    """
    if not input_str:
        return ""

    return (
        input_str.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("<br>", "\n")
        .replace("&#039;", "'")
        .replace("&quot;", '"')
    )


async def async_pool(
    pool_limit: int, array: list[T], iterator_fn: Callable[[T], Awaitable[R]]
) -> list[R]:
    """Execute async operations with concurrency limit.

    Args:
        pool_limit: Maximum number of concurrent operations
        array: List of items to process
        iterator_fn: Async function to apply to each item

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(pool_limit)

    async def bounded_operation(item: T) -> R:
        async with semaphore:
            return await iterator_fn(item)

    tasks = [bounded_operation(item) for item in array]
    return await asyncio.gather(*tasks, return_exceptions=False)


def get_random_string(length: int) -> str:
    """Generate random string of specified length.

    Args:
        length: Length of string to generate

    Returns:
        Random string
    """
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def abs_url(url: str, base: str) -> str:
    """Convert relative URL to absolute URL.

    Args:
        url: URL to convert
        base: Base URL

    Returns:
        Absolute URL
    """
    if re.match(r"^\w+://", url):
        return url
    if url.startswith("/"):
        return base[: base.rfind("/") + 1] + url[1:]
    return base[: base.rfind("/") + 1] + url
