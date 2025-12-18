"""
Comprehensive test suite for AniWorld and SerienStream API endpoints.

This module tests all API endpoints for the aniworld and serienstream providers
to ensure they return valid responses and the providers are functioning correctly.

Tests cover:
- Sources API: /sources/, /{source}/preferences, /{source}/popular, etc.
- Series API: /{source}/series, /{source}/series/seasons, etc.
"""

import pytest
from httpx import AsyncClient


class TestSourcesEndpoints:
    """Tests for the /sources API endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_sources(self, async_client: AsyncClient):
        """Test GET /sources/ returns available sources."""
        response = await async_client.get("/sources/")

        assert response.status_code == 200
        data = response.json()

        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "aniworld" in data["sources"]
        assert "serienstream" in data["sources"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source", ["aniworld", "serienstream"])
    async def test_get_source_preferences(self, async_client: AsyncClient, source: str):
        """Test GET /sources/{source}/preferences returns valid preferences."""
        response = await async_client.get(f"/sources/{source}/preferences")

        assert response.status_code == 200
        data = response.json()

        assert "preferences" in data
        assert isinstance(data["preferences"], dict)

        # Check for expected preference keys
        pref_keys = data["preferences"].keys()
        assert len(pref_keys) > 0, "Should have at least one preference"

        # Validate preference structure
        for key, pref in data["preferences"].items():
            assert "key" in pref
            assert pref["key"] == key

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_preferences_invalid_source(self, async_client: AsyncClient):
        """Test GET /sources/{source}/preferences with invalid source returns 404."""
        response = await async_client.get("/sources/invalid_source/preferences")
        assert response.status_code == 404


class TestPopularEndpoints:
    """Tests for the popular content endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source,expected_type", [
        ("aniworld", "anime"),
        ("serienstream", "normal"),
    ])
    async def test_get_popular_content(
        self, async_client: AsyncClient, source: str, expected_type: str
    ):
        """Test GET /sources/{source}/popular returns valid paginated results."""
        response = await async_client.get(f"/sources/{source}/popular")

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "type" in data
        assert data["type"] == expected_type
        assert "list" in data
        assert "has_next_page" in data
        assert isinstance(data["list"], list)

        # Should have some results
        assert len(data["list"]) > 0, f"Popular should return results for {source}"

        # Validate search result structure
        for item in data["list"][:3]:  # Check first 3 items
            assert "name" in item
            assert "image_url" in item
            assert "link" in item
            assert "provider" in item
            # Provider name may be capitalized (e.g., "AniWorld" vs "aniworld")
            assert item["provider"].lower() == source.lower()
            assert item["name"], "Name should not be empty"
            assert item["link"], "Link should not be empty"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source", ["aniworld", "serienstream"])
    async def test_get_popular_pagination(self, async_client: AsyncClient, source: str):
        """Test GET /sources/{source}/popular with page parameter."""
        response = await async_client.get(f"/sources/{source}/popular", params={"page": 1})

        assert response.status_code == 200
        data = response.json()

        assert "list" in data
        assert isinstance(data["list"], list)


class TestLatestEndpoints:
    """Tests for the latest updates endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source,expected_type", [
        ("aniworld", "anime"),
        ("serienstream", "normal"),
    ])
    async def test_get_latest_updates(
        self, async_client: AsyncClient, source: str, expected_type: str
    ):
        """Test GET /sources/{source}/latest returns valid paginated results."""
        response = await async_client.get(f"/sources/{source}/latest")

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "type" in data
        assert data["type"] == expected_type
        assert "list" in data
        assert "has_next_page" in data
        assert isinstance(data["list"], list)

        # Should have some results
        assert len(data["list"]) > 0, f"Latest should return results for {source}"

        # Validate search result structure
        for item in data["list"][:3]:  # Check first 3 items
            assert "name" in item
            assert "image_url" in item
            assert "link" in item
            assert "provider" in item


class TestSearchEndpoints:
    """Tests for the search endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_aniworld(self, async_client: AsyncClient, aniworld_test_data):
        """Test GET /sources/aniworld/search returns valid results."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/search",
            params={"q": aniworld_test_data["search_query"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert data["type"] == "anime"
        assert "list" in data
        assert isinstance(data["list"], list)

        # Should find results for the search query
        assert len(data["list"]) > 0, "Search should return results"

        # Validate first result
        if data["list"]:
            first_result = data["list"][0]
            assert "name" in first_result
            assert "link" in first_result
            assert "provider" in first_result
            # Provider name may be capitalized (e.g., "AniWorld" vs "aniworld")
            assert first_result["provider"].lower() == "aniworld"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_serienstream(self, async_client: AsyncClient, serienstream_test_data):
        """Test GET /sources/serienstream/search returns valid results."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/search",
            params={"q": serienstream_test_data["search_query"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert data["type"] == "normal"
        assert "list" in data
        assert isinstance(data["list"], list)

        # Should find results for the search query
        assert len(data["list"]) > 0, "Search should return results"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_search_empty_query(self, async_client: AsyncClient):
        """Test GET /sources/{source}/search with empty query returns error."""
        response = await async_client.get("/sources/aniworld/search", params={"q": ""})
        # FastAPI should return 422 for validation error (min_length=1)
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source", ["aniworld", "serienstream"])
    async def test_search_no_results(self, async_client: AsyncClient, source: str):
        """Test GET /sources/{source}/search with nonsense query returns empty list."""
        response = await async_client.get(
            f"/sources/{source}/search",
            params={"q": "xyznonexistentquery12345"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "list" in data
        # May or may not find results, but should be a valid response
        assert isinstance(data["list"], list)


class TestSeriesEndpoints:
    """Tests for the series detail endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_overview_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/series returns series overview."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "type" in data
        assert data["type"] == "anime"
        assert "series" in data

        series = data["series"]
        assert "slug" in series
        assert "seasons" in series
        assert "movies" in series

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_overview_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/series returns series overview."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/series",
            params={"url": serienstream_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert data["type"] == "normal"
        assert "series" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_seasons_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/series/seasons returns all seasons."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "seasons" in data
        assert isinstance(data["seasons"], list)

        # Should have at least one season
        assert len(data["seasons"]) > 0, "Should have at least one season"

        # Validate season structure
        for season in data["seasons"]:
            assert "season" in season
            assert "episodes" in season
            assert isinstance(season["episodes"], list)

            # Validate episodes if present
            for episode in season["episodes"][:3]:  # Check first 3 episodes
                assert "title" in episode
                assert "url" in episode

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_seasons_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/series/seasons returns all seasons."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/series/seasons",
            params={"url": serienstream_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "seasons" in data
        assert isinstance(data["seasons"], list)
        assert len(data["seasons"]) > 0


class TestSeasonEndpoints:
    """Tests for specific season endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_specific_season_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/series/seasons/{season_num} returns specific season."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/{aniworld_test_data['season_num']}",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "season" in data

        season = data["season"]
        assert "season" in season
        assert season["season"] == aniworld_test_data["season_num"]
        assert "episodes" in season
        assert len(season["episodes"]) > 0, "Season should have episodes"

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_specific_season_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/series/seasons/{season_num} returns specific season."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/series/seasons/{serienstream_test_data['season_num']}",
            params={"url": serienstream_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "season" in data
        assert data["season"]["season"] == serienstream_test_data["season_num"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_nonexistent_season(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/{source}/series/seasons/{season_num} with invalid season returns 404."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/999",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 404


class TestEpisodeEndpoints:
    """Tests for specific episode endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_specific_episode_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/series/seasons/.../episodes/... returns specific episode."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/{aniworld_test_data['season_num']}/episodes/{aniworld_test_data['episode_num']}",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "episode" in data

        episode = data["episode"]
        assert "title" in episode
        assert "url" in episode
        assert episode["episode"] == aniworld_test_data["episode_num"]
        assert episode["season"] == aniworld_test_data["season_num"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_specific_episode_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/series/seasons/.../episodes/... returns specific episode."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/series/seasons/{serienstream_test_data['season_num']}/episodes/{serienstream_test_data['episode_num']}",
            params={"url": serienstream_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "episode" in data
        episode = data["episode"]
        assert "title" in episode
        assert "url" in episode

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_nonexistent_episode(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET episode with invalid episode number returns 404."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/1/episodes/999",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 404


class TestMoviesEndpoints:
    """Tests for movies/OVAs endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_movies_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/series/movies returns movies list."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/movies",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "movies" in data
        assert isinstance(data["movies"], list)

        # Validate movie structure if movies exist
        for movie in data["movies"][:3]:
            assert "number" in movie
            assert "title" in movie
            assert "kind" in movie
            assert "url" in movie
            assert movie["kind"] in ["movie", "ova", "special"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_series_movies_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/series/movies returns movies list."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/series/movies",
            params={"url": serienstream_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "movies" in data
        assert isinstance(data["movies"], list)


class TestVideoEndpoints:
    """Tests for video extraction endpoints."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_video_sources_aniworld(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/aniworld/videos returns video sources."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/videos",
            params={"url": aniworld_test_data["episode_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "videos" in data
        assert isinstance(data["videos"], list)

        # Validate video source structure if videos exist
        for video in data["videos"][:3]:
            assert "url" in video
            assert "quality" in video

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_video_sources_serienstream(
        self, async_client: AsyncClient, serienstream_test_data
    ):
        """Test GET /sources/serienstream/videos returns video sources."""
        response = await async_client.get(
            f"/sources/{serienstream_test_data['source']}/videos",
            params={"url": serienstream_test_data["episode_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert "type" in data
        assert "videos" in data
        assert isinstance(data["videos"], list)

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_get_video_sources_with_lang_filter(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test GET /sources/{source}/videos with language filter."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/videos",
            params={
                "url": aniworld_test_data["episode_url"],
                "lang": "de",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "videos" in data
        assert isinstance(data["videos"], list)


class TestTMDBEnrichment:
    """Tests for TMDB enrichment in responses."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_series_overview_has_tmdb_data(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test that series overview includes TMDB data when available."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        # TMDB data may or may not be present depending on API availability
        # Just verify the field exists in the response
        assert "tmdb_data" in data
        assert "match_confidence" in data

        # If TMDB data is present, validate its structure
        if data["tmdb_data"]:
            tmdb = data["tmdb_data"]
            assert "id" in tmdb
            # Should have name or title depending on media type
            assert "name" in tmdb or "title" in tmdb

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_season_has_tmdb_enrichment(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test that specific season includes TMDB season data when available."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/{aniworld_test_data['season_num']}",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify TMDB fields exist
        assert "tmdb_data" in data
        assert "tmdb_season" in data

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_episode_has_tmdb_enrichment(
        self, async_client: AsyncClient, aniworld_test_data
    ):
        """Test that specific episode includes TMDB episode data when available."""
        response = await async_client.get(
            f"/sources/{aniworld_test_data['source']}/series/seasons/{aniworld_test_data['season_num']}/episodes/{aniworld_test_data['episode_num']}",
            params={"url": aniworld_test_data["series_url"]},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify TMDB fields exist
        assert "tmdb_data" in data
        assert "tmdb_episode" in data


class TestErrorHandling:
    """Tests for error handling scenarios."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_source_returns_404(self, async_client: AsyncClient):
        """Test that invalid source returns 404."""
        response = await async_client.get("/sources/nonexistent_source/popular")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_missing_url_param_returns_422(self, async_client: AsyncClient):
        """Test that missing required URL parameter returns 422."""
        response = await async_client.get("/sources/aniworld/series")
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_page_param_returns_422(self, async_client: AsyncClient):
        """Test that invalid page parameter returns 422."""
        response = await async_client.get(
            "/sources/aniworld/popular", params={"page": 0}
        )
        assert response.status_code == 422

        response = await async_client.get(
            "/sources/aniworld/popular", params={"page": -1}
        )
        assert response.status_code == 422


class TestResponseTypes:
    """Tests to validate response type consistency."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source,expected_type", [
        ("aniworld", "anime"),
        ("serienstream", "normal"),
    ])
    async def test_popular_response_type(
        self, async_client: AsyncClient, source: str, expected_type: str
    ):
        """Test that popular endpoint returns correct type."""
        response = await async_client.get(f"/sources/{source}/popular")
        assert response.status_code == 200
        assert response.json()["type"] == expected_type

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source,expected_type", [
        ("aniworld", "anime"),
        ("serienstream", "normal"),
    ])
    async def test_latest_response_type(
        self, async_client: AsyncClient, source: str, expected_type: str
    ):
        """Test that latest endpoint returns correct type."""
        response = await async_client.get(f"/sources/{source}/latest")
        assert response.status_code == 200
        assert response.json()["type"] == expected_type

    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.parametrize("source,expected_type", [
        ("aniworld", "anime"),
        ("serienstream", "normal"),
    ])
    async def test_search_response_type(
        self, async_client: AsyncClient, source: str, expected_type: str
    ):
        """Test that search endpoint returns correct type."""
        response = await async_client.get(
            f"/sources/{source}/search", params={"q": "test"}
        )
        assert response.status_code == 200
        assert response.json()["type"] == expected_type
