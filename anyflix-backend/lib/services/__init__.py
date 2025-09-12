"""Services for streaming media backend."""

from .anilist_service import AniListService
from .media_service import MediaService
from .metadata_service import MetadataEnrichmentService

# Backward compatibility alias
AnimeService = MediaService

__all__ = [
    "MediaService",
    "AnimeService",  # Backward compatibility
    "AniListService",
    "MetadataEnrichmentService",
]
