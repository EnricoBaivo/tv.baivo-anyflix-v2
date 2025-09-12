"""Shared mixins for model composition."""

from typing import Optional

from pydantic import BaseModel, Field

from .anilist import Media as AniListMedia


class AniListMixin(BaseModel):
    """Mixin for AniList metadata integration."""

    anilist_data: Optional[AniListMedia] = None
    anilist_id: Optional[int] = None
    match_confidence: Optional[float] = Field(
        None, description="Confidence score for AniList match (0.0-1.0)"
    )


class EnhancedMetadataMixin(BaseModel):
    """Mixin for enhanced metadata derived from AniList."""

    enhanced_title: Optional[str] = Field(
        None, description="Preferred title from AniList"
    )
    enhanced_description: Optional[str] = Field(
        None, description="Rich description from AniList"
    )
    enhanced_genres: Optional[list[str]] = Field(
        None, description="Comprehensive genre list from AniList"
    )
    score: Optional[int] = Field(None, description="AniList average score (0-100)")
    popularity: Optional[int] = Field(None, description="AniList popularity ranking")
    year: Optional[int] = Field(None, description="Release year")
    season: Optional[str] = Field(None, description="Release season")
    status_text: Optional[str] = Field(None, description="Human readable status")
    studios: Optional[list[str]] = Field(None, description="Animation studios")
    external_links: Optional[list[dict]] = Field(
        None, description="Official and streaming links"
    )


class DetailedMetadataMixin(EnhancedMetadataMixin):
    """Extended metadata mixin for detailed views."""

    episode_count: Optional[int] = Field(
        None, description="Total episode count from AniList"
    )
    characters: Optional[list[dict]] = Field(
        None, description="Main characters with voice actors"
    )
    staff: Optional[list[dict]] = Field(None, description="Staff information")
    relations: Optional[list[dict]] = Field(None, description="Related anime/manga")
    recommendations: Optional[list[dict]] = Field(
        None, description="Recommended similar anime"
    )
    tags: Optional[list[dict]] = Field(
        None, description="Content tags with descriptions"
    )
