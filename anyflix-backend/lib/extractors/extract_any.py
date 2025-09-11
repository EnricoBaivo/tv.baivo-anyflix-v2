"""Extract Any video extractor dispatcher."""

from typing import Awaitable, Callable, Dict, List, Optional

from ..models.base import VideoSource

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
    elif "englisch" in lang_lower or "english" in lang_lower:
        return "en"
    else:
        return "sub"  # Default fallback


async def extract_any(
    url: str,
    method: str,
    headers: Optional[Dict[str, str]] = None,
) -> List[VideoSource]:
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

    logger.info(f"extract_any called with method={method}, url={url}")
    extractor_func = EXTRACTOR_METHODS.get(method.lower())
    if not extractor_func:
        logger.warning(f"No extractor found for method: {method}")
        return []

    try:
        logger.info(f"Using extractor: {extractor_func.__name__}")
        # Call the appropriate extractor
        video_sources = await extractor_func(url, headers)

        logger.info(f"Extractor returned {len(video_sources)} videos")
        return video_sources

    except Exception as e:
        # If extraction fails, return empty list
        logger.error(f"Extraction failed for {method}: {e}")
        return []


# No wrapper needed - voe_extractor is already async


# Mapping of extractor methods to their implementations
EXTRACTOR_METHODS: Dict[
    str, Callable[[str, Optional[Dict[str, str]]], Awaitable[List[VideoSource]]]
] = {
    "doodstream": dood_extractor,
    "filemoon": filemoon_extractor,
    "luluvdo": luluvdo_extractor,
    "speedfiles": speedfiles_extractor,
    "vidmoly": vidmoly_extractor,
    "vidoza": vidoza_extractor,
    "voe": voe_extractor,
}
