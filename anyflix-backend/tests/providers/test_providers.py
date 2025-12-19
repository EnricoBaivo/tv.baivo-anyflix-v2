"""
Direct provider tests for AniWorld and SerienStream.

This module tests the provider classes directly without going through the API layer.
These tests validate the core functionality of the providers:
- HTML parsing and data extraction
- Search functionality
- Popular/Latest content retrieval
- Video extraction
"""

import pytest

from lib.providers.aniworld import AniWorldProvider
from lib.providers.serienstream import SerienStreamProvider


class TestAniWorldProvider:
    """Tests for the AniWorld provider."""

    @pytest.fixture
    def provider(self):
        """Create AniWorld provider instance."""
        return AniWorldProvider()

    @pytest.fixture
    def test_series_url(self):
        """Return a known anime series URL for testing."""
        return "https://aniworld.to/anime/stream/one-punch-man"

    @pytest.fixture
    def test_episode_url(self):
        """Return a known episode URL for testing."""
        return "https://aniworld.to/anime/stream/one-punch-man/staffel-1/episode-1"

    def test_provider_properties(self, provider):
        """Test provider basic properties."""
        assert provider.source.name == "AniWorld"
        assert provider.source.base_url == "https://aniworld.to"
        assert provider.content_type.value == "anime"

    def test_get_source_preferences(self, provider):
        """Test that source preferences are returned correctly."""
        preferences = provider.get_source_preferences()

        assert preferences is not None
        assert isinstance(preferences, list)
        assert len(preferences) > 0

        # Check that we have the expected preference keys
        pref_keys = [p.key for p in preferences]
        # Actual keys from the provider
        assert "lang" in pref_keys
        assert "type" in pref_keys
        assert "res" in pref_keys or "host" in pref_keys

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search(self, provider):
        """Test search functionality."""
        async with provider:
            result = await provider.search("one punch", page=1)

        assert result is not None
        assert hasattr(result, "items")
        assert hasattr(result, "pagination")
        assert hasattr(result, "content_type")
        assert result.content_type.value == "anime"

        # Should find results for "one punch"
        assert len(result.items) > 0, "Should find results for 'one punch'"

        # Validate first result structure
        first = result.items[0]
        assert first.name
        assert first.link
        # Provider name is the actual source name from the provider
        assert first.provider in ["aniworld", "AniWorld"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_popular(self, provider):
        """Test get_popular functionality."""
        async with provider:
            result = await provider.get_popular(page=1)

        assert result is not None
        assert result.content_type.value == "anime"
        assert len(result.items) > 0, "Popular should return results"

        # Validate result structure
        for item in result.items[:5]:
            assert item.name
            assert item.link
            assert item.image_url

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_latest_updates(self, provider):
        """Test get_latest_updates functionality."""
        async with provider:
            result = await provider.get_latest_updates(page=1)

        assert result is not None
        assert result.content_type.value == "anime"
        assert len(result.items) > 0, "Latest updates should return results"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_detail(self, provider, test_series_url):
        """Test get_detail functionality."""
        async with provider:
            result = await provider.get_detail(test_series_url, episodes=True)

        assert result is not None
        assert result.name
        assert result.cover_image_url
        assert result.description

        # Should have episodes
        assert len(result.episodes) > 0, "Should have episodes"

        # Validate episode structure
        for ep in result.episodes[:3]:
            assert ep.title
            assert ep.url

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_detail_without_episodes(self, provider, test_series_url):
        """Test get_detail without fetching episodes."""
        async with provider:
            result = await provider.get_detail(test_series_url, episodes=False)

        assert result is not None
        assert result.name
        # Episodes list should be empty when episodes=False
        assert len(result.episodes) == 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_video_list(self, provider, test_episode_url):
        """Test get_video_list functionality."""
        async with provider:
            result = await provider.get_video_list(test_episode_url)

        assert result is not None
        assert hasattr(result, "videos")
        assert isinstance(result.videos, list)

        # Validate video source structure if videos exist
        for video in result.videos[:3]:
            assert video.url
            assert video.quality


class TestSerienStreamProvider:
    """Tests for the SerienStream provider."""

    @pytest.fixture
    def provider(self):
        """Create SerienStream provider instance."""
        return SerienStreamProvider()

    @pytest.fixture
    def test_series_url(self):
        """Return a known TV series URL for testing."""
        return "https://serienstream.to/serie/stream/the-witcher"

    @pytest.fixture
    def test_episode_url(self):
        """Return a known episode URL for testing."""
        return "https://serienstream.to/serie/stream/the-witcher/staffel-1/episode-1"

    def test_provider_properties(self, provider):
        """Test provider basic properties."""
        assert provider.source.name == "SerienStream"
        assert provider.source.base_url == "https://serienstream.to"
        assert provider.content_type.value == "series_movie"

    def test_get_source_preferences(self, provider):
        """Test that source preferences are returned correctly."""
        preferences = provider.get_source_preferences()

        assert preferences is not None
        assert isinstance(preferences, list)
        assert len(preferences) > 0

        pref_keys = [p.key for p in preferences]
        assert "lang" in pref_keys
        assert "type" in pref_keys

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search(self, provider):
        """Test search functionality."""
        async with provider:
            result = await provider.search("witcher", page=1)

        assert result is not None
        assert result.content_type.value == "series_movie"
        assert len(result.items) > 0, "Should find results for 'witcher'"

        first = result.items[0]
        assert first.name
        assert first.link
        assert first.provider in ["serienstream", "SerienStream"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_popular(self, provider):
        """Test get_popular functionality."""
        async with provider:
            result = await provider.get_popular(page=1)

        assert result is not None
        assert result.content_type.value == "series_movie"
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_latest_updates(self, provider):
        """Test get_latest_updates functionality."""
        async with provider:
            result = await provider.get_latest_updates(page=1)

        assert result is not None
        assert result.content_type.value == "series_movie"
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_detail(self, provider, test_series_url):
        """Test get_detail functionality."""
        async with provider:
            result = await provider.get_detail(test_series_url, episodes=True)

        assert result is not None
        assert result.name
        assert result.cover_image_url

        # Should have episodes
        assert len(result.episodes) > 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_video_list(self, provider, test_episode_url):
        """Test get_video_list functionality."""
        async with provider:
            result = await provider.get_video_list(test_episode_url)

        assert result is not None
        assert hasattr(result, "videos")
        assert isinstance(result.videos, list)


class TestProviderContextManager:
    """Tests for provider context manager functionality."""

    @pytest.mark.asyncio
    async def test_aniworld_context_manager(self):
        """Test AniWorld provider context manager."""
        provider = AniWorldProvider()

        # Should work with async context manager
        async with provider:
            assert provider.client is not None

        # Client should be closed after exiting context
        # (Implementation detail may vary)

    @pytest.mark.asyncio
    async def test_serienstream_context_manager(self):
        """Test SerienStream provider context manager."""
        provider = SerienStreamProvider()

        async with provider:
            assert provider.client is not None


class TestSearchResultStructure:
    """Tests to validate search result data structure."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_aniworld_search_result_has_media_info(self):
        """Test that AniWorld search results include media_info."""
        provider = AniWorldProvider()

        async with provider:
            result = await provider.search("one punch", page=1)

        if result.items:
            first = result.items[0]
            # media_info should be present (may be None for lightweight results)
            assert hasattr(first, "media_info")
            # available_languages should be present
            assert hasattr(first, "available_languages")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_serienstream_search_result_has_media_info(self):
        """Test that SerienStream search results include media_info."""
        provider = SerienStreamProvider()

        async with provider:
            result = await provider.search("witcher", page=1)

        if result.items:
            first = result.items[0]
            assert hasattr(first, "media_info")
            assert hasattr(first, "available_languages")


class TestEpisodeParsing:
    """Tests for episode parsing functionality."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_aniworld_episode_parsing(self):
        """Test that AniWorld correctly parses episode data."""
        provider = AniWorldProvider()
        url = "https://aniworld.to/anime/stream/one-punch-man"

        async with provider:
            result = await provider.get_detail(url, episodes=True)

        # Find season 1 episodes
        season_1_eps = [ep for ep in result.episodes if ep.season == 1]
        assert len(season_1_eps) > 0, "Should have season 1 episodes"

        # Validate episode numbers are sequential
        ep_numbers = sorted([ep.episode for ep in season_1_eps if ep.episode])
        assert ep_numbers[0] == 1, "First episode should be 1"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_serienstream_episode_parsing(self):
        """Test that SerienStream correctly parses episode data."""
        provider = SerienStreamProvider()
        url = "https://serienstream.to/serie/stream/the-witcher"

        async with provider:
            result = await provider.get_detail(url, episodes=True)

        season_1_eps = [ep for ep in result.episodes if ep.season == 1]
        assert len(season_1_eps) > 0

        # Episodes should have valid URLs (may be relative or absolute)
        for ep in season_1_eps:
            # URL should contain expected path segments
            assert "/staffel-" in ep.url or "/episode-" in ep.url
            # URL should not be empty
            assert ep.url, "Episode URL should not be empty"


class TestLanguageHandling:
    """Tests for language filtering and detection."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_aniworld_language_filter(self):
        """Test AniWorld video extraction with language filter."""
        provider = AniWorldProvider()
        url = "https://aniworld.to/anime/stream/one-punch-man/staffel-1/episode-1"

        async with provider:
            # Get all videos
            all_videos = await provider.get_video_list(url)

            # Get German only
            de_videos = await provider.get_video_list(url, lang_filter="de")

        # Both should return valid responses
        assert all_videos is not None
        assert de_videos is not None

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_serienstream_language_filter(self):
        """Test SerienStream video extraction with language filter."""
        provider = SerienStreamProvider()
        url = "https://serienstream.to/serie/stream/the-witcher/staffel-1/episode-1"

        async with provider:
            all_videos = await provider.get_video_list(url)
            de_videos = await provider.get_video_list(url, lang_filter="de")

        assert all_videos is not None
        assert de_videos is not None
