"""Unit tests for AnimeService."""

from unittest.mock import Mock, patch

import pytest

from lib.models.base import SourcePreference
from lib.services.anime_service import AnimeService


class TestAnimeService:
    """Test cases for AnimeService."""

    def test_get_available_sources(self, anime_service):
        """Test getting available sources."""
        sources = anime_service.get_available_sources()
        assert isinstance(sources, list)
        assert "aniworld" in sources
        assert "serienstream" in sources
        assert len(sources) == 2

    def test_get_provider_valid_source(self, anime_service):
        """Test getting a valid provider."""
        provider = anime_service.get_provider("aniworld")
        assert provider is not None
        assert provider.source.name == "AniWorld"

    def test_get_provider_invalid_source(self, anime_service):
        """Test getting an invalid provider."""
        provider = anime_service.get_provider("nonexistent")
        assert provider is None

    def test_get_source_preferences_aniworld(self, anime_service):
        """Test getting source preferences for AniWorld."""
        preferences = anime_service.get_source_preferences("aniworld")

        assert isinstance(preferences, list)
        assert len(preferences) == 6  # lang, type, res, host, lang_filter, host_filter

        # Check first preference (language)
        lang_pref = preferences[0]
        assert isinstance(lang_pref, SourcePreference)
        assert lang_pref.key == "lang"
        assert lang_pref.list_preference is not None
        assert lang_pref.list_preference["title"] == "Bevorzugte Sprache"
        assert "Deutsch" in lang_pref.list_preference["entries"]
        assert "Englisch" in lang_pref.list_preference["entries"]

    def test_get_source_preferences_serienstream(self, anime_service):
        """Test getting source preferences for SerienStream."""
        preferences = anime_service.get_source_preferences("serienstream")

        assert isinstance(preferences, list)
        assert len(preferences) == 6  # Same structure as AniWorld

        # Check that it's properly configured
        lang_pref = next((p for p in preferences if p.key == "lang"), None)
        assert lang_pref is not None
        assert lang_pref.list_preference["title"] == "Bevorzugte Sprache"

    def test_get_source_preferences_invalid_source(self, anime_service):
        """Test getting preferences for invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            anime_service.get_source_preferences("invalid")

    def test_get_source_preferences_structure(self, anime_service):
        """Test the structure of source preferences."""
        preferences = anime_service.get_source_preferences("aniworld")

        # Check each preference type
        expected_keys = ["lang", "type", "res", "host", "lang_filter", "host_filter"]
        actual_keys = [p.key for p in preferences]

        for key in expected_keys:
            assert key in actual_keys

        # Check list preferences vs multi-select preferences
        for pref in preferences:
            if pref.key in ["lang", "type", "res", "host"]:
                assert pref.list_preference is not None
                assert pref.multi_select_list_preference is None
                assert "title" in pref.list_preference
                assert "entries" in pref.list_preference
                assert "entryValues" in pref.list_preference
            elif pref.key in ["lang_filter", "host_filter"]:
                assert pref.list_preference is None
                assert pref.multi_select_list_preference is not None
                assert "title" in pref.multi_select_list_preference
                assert "entries" in pref.multi_select_list_preference
                assert "values" in pref.multi_select_list_preference

    @pytest.mark.asyncio
    async def test_get_popular_invalid_source(self, anime_service):
        """Test get_popular with invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            await anime_service.get_popular("invalid")

    @pytest.mark.asyncio
    async def test_get_latest_updates_invalid_source(self, anime_service):
        """Test get_latest_updates with invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            await anime_service.get_latest_updates("invalid")

    @pytest.mark.asyncio
    async def test_search_invalid_source(self, anime_service):
        """Test search with invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            await anime_service.search("invalid", "test query")

    @pytest.mark.asyncio
    async def test_get_detail_invalid_source(self, anime_service):
        """Test get_detail with invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            await anime_service.get_detail("invalid", "/test/url")

    @pytest.mark.asyncio
    async def test_get_video_list_invalid_source(self, anime_service):
        """Test get_video_list with invalid source."""
        with pytest.raises(ValueError, match="Source 'invalid' not found"):
            await anime_service.get_video_list("invalid", "/test/url")
