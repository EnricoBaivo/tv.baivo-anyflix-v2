"""Shared provider registry for all routers.

This module provides a centralized registry for:
- Media source providers (AniWorld, SerienStream)
- TMDB services for metadata enrichment

All routers should import providers and services from here
to ensure single instances and consistent configuration.
"""

import logging

from fastapi import HTTPException

from app.config import settings
from lib.providers.aniworld import AniWorldProvider
from lib.providers.base import BaseProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.tmdb_enrichment_service import TMDBEnrichmentService
from lib.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

# Initialize providers with proper typing
providers: dict[str, BaseProvider] = {
    "aniworld": AniWorldProvider(),
    "serienstream": SerienStreamProvider(),
}

# Initialize TMDB services with validation
_tmdb_api_key = settings.tmdb_api_key
if not _tmdb_api_key:
    logger.warning(
        "TMDB_API_KEY not configured. TMDB metadata enrichment will be disabled."
    )

tmdb_service = TMDBService(api_key=_tmdb_api_key)
enrichment_service = TMDBEnrichmentService(tmdb_service)


def get_provider(source: str) -> BaseProvider:
    """Get provider by source name.

    Args:
        source: The source name (e.g., 'aniworld', 'serienstream')

    Returns:
        BaseProvider: The provider instance for the given source

    Raises:
        HTTPException: If the source is not found (404)
    """
    if source not in providers:
        raise HTTPException(status_code=404, detail=f"Source '{source}' not found")
    return providers[source]
