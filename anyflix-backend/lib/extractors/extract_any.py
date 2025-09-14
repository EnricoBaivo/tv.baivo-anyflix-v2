"""Extract Any video extractor dispatcher."""

from collections.abc import Awaitable, Callable

from lib.models.base import VideoSource

# Import all implemented extractors
from .dood_extractor import dood_extractor
from .filemoon_extractor import filemoon_extractor
from .luluvdo_extractor import luluvdo_extractor
from .speedfiles_extractor import speedfiles_extractor
from .vidmoly_extractor import vidmoly_extractor
from .vidoza_extractor import vidoza_extractor
from .voe_extractor import voe_extractor


def _map_language_to_code(lang: str) -> str:
    """
    Map language names to standard language codes.

    Args:
        lang: Language name (e.g., 'Deutsch', 'Englisch')

    Returns:
        Standard language code (e.g., 'de', 'en')
    """
    lang_lower = lang.lower()
    if "deutsch" in lang_lower:
        return "de"
    if "englisch" in lang_lower or "english" in lang_lower:
        return "en"
    return "sub"  # Default fallback


async def extract_any(
    url: str,
    method: str,
    headers: dict[str, str] | None = None,
) -> list[VideoSource]:
    """
    Extract video sources from any supported host.

    This function dispatches to the appropriate extractor based on the method.
    It mimics the extractAny function from the JavaScript helpers.

    Args:
        url: The video URL to extract from
        method: The extraction method/host type
        headers: Optional HTTP headers

    Returns:
        List of VideoSource objects
    """
    import logging

    logger = logging.getLogger(__name__)

    logger.info("extract_any called with method=%s, url=%s", method, url)
    extractor_func = EXTRACTOR_METHODS.get(method.lower())
    if not extractor_func:
        logger.warning("No extractor found for method: %s", method)
        return []

    try:
        logger.info("Using extractor: %s", extractor_func.__name__)
        # Call the appropriate extractor
        video_sources = await extractor_func(url, headers)

        logger.info("Extractor returned %d videos", len(video_sources))
    except Exception:
        # If extraction fails, return empty list
        logger.exception("Extraction failed for %s", method)
        return []
    else:
        return video_sources


# No wrapper needed - voe_extractor is already async


# Mapping of extractor methods to their implementations
EXTRACTOR_METHODS: dict[
    str, Callable[[str, dict[str, str] | None], Awaitable[list[VideoSource]]]
] = {
    "doodstream": dood_extractor,
    "filemoon": filemoon_extractor,
    "luluvdo": luluvdo_extractor,
    "speedfiles": speedfiles_extractor,
    "vidmoly": vidmoly_extractor,
    "vidoza": vidoza_extractor,
    "voe": voe_extractor,
}
