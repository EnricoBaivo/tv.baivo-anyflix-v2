"""URL utilities for proper URL handling and construction."""

from urllib.parse import urljoin, urlparse


def normalize_url(base_url: str, path: str) -> str:
    """Normalize URL by properly joining base URL and path.

    This function handles:
    - Absolute URLs (returns as-is)
    - Relative URLs starting with / (joins with base)
    - Relative URLs without / (joins with base + /)

    Args:
        base_url: Base URL (e.g., "https://example.com")
        path: Path to join (absolute URL, /path, or path)

    Returns:
        Properly constructed URL

    Examples:
        >>> normalize_url("https://aniworld.to", "https://aniworld.to/anime/stream/test")
        "https://aniworld.to/anime/stream/test"
        >>> normalize_url("https://aniworld.to", "/anime/stream/test")
        "https://aniworld.to/anime/stream/test"
        >>> normalize_url("https://aniworld.to", "anime/stream/test")
        "https://aniworld.to/anime/stream/test"
    """
    # If path is already an absolute URL, return it as-is
    if path.startswith(("http://", "https://")):
        return path

    # Use urllib.parse.urljoin for proper URL joining
    # This handles all edge cases properly
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def is_absolute_url(url: str) -> bool:
    """Check if URL is absolute.

    Args:
        url: URL to check

    Returns:
        True if URL is absolute, False otherwise
    """
    return url.startswith(("http://", "https://"))


def get_domain(url: str) -> str:
    """Extract domain from URL.

    Args:
        url: URL to extract domain from

    Returns:
        Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
