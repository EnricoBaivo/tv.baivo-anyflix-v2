"""Integration tests for hierarchical API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_anime_service, get_enhanced_anime_service
from app.main import app
from lib.models.base import Episode, MediaInfo, Movie, MovieKind, Season, SeriesDetail
from lib.models.responses import DetailResponse, SeriesDetailResponse


@pytest.fixture
def mock_anime_service():
    """Mock anime service for testing."""
    service = AsyncMock()
    # Override the FastAPI dependency for both services
    app.dependency_overrides[get_anime_service] = lambda: service
    app.dependency_overrides[get_enhanced_anime_service] = lambda: service
    yield service
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_detail_response():
    """Sample detail response with flat episodes."""
    return DetailResponse(
        media=MediaInfo(
            name="Attack on Titan",
            image_url="https://example.com/image.jpg",
            description="Test description",
            author="Test Author",
            status=5,
            genre=["Action", "Drama"],
            episodes=[
                {
                    "name": "Staffel 4 Folge 30 : The Final Chapter Part 2 [Series Final Episode]",
                    "url": "/anime/stream/attack-on-titan/staffel-4/episode-30",
                    "date_upload": None,
                },
                {
                    "name": "Staffel 4 Folge 29 : The Final Chapter Part 1",
                    "url": "/anime/stream/attack-on-titan/staffel-4/episode-29",
                    "date_upload": None,
                },
                {
                    "name": "Staffel 3 Folge 1 : Smoke Signal",
                    "url": "/anime/stream/attack-on-titan/staffel-3/episode-1",
                    "date_upload": None,
                },
                {
                    "name": "Staffel 1 Folge 1 : To You, in 2000 Years",
                    "url": "/anime/stream/attack-on-titan/staffel-1/episode-1",
                    "date_upload": None,
                },
                {
                    "name": "Film 12 : The Last Attack [Movie]",
                    "url": "/anime/stream/attack-on-titan/filme/film-12",
                    "date_upload": None,
                },
                {
                    "name": "Film 11 : Great need [OVA]",
                    "url": "/anime/stream/attack-on-titan/filme/film-11",
                    "date_upload": None,
                },
            ],
        )
    )


@pytest.fixture
def sample_series_detail_response():
    """Sample hierarchical series detail response."""
    return SeriesDetailResponse(
        series=SeriesDetail(
            slug="attack-on-titan",
            seasons=[
                Season(
                    season=1,
                    title="Staffel 1",
                    episodes=[
                        Episode(
                            season=1,
                            episode=1,
                            title="To You, in 2000 Years",
                            url="/anime/stream/attack-on-titan/staffel-1/episode-1",
                            date_upload=None,
                            tags=[],
                        ),
                        Episode(
                            season=1,
                            episode=25,
                            title="Wall - Assault on Stohess Part 3",
                            url="/anime/stream/attack-on-titan/staffel-1/episode-25",
                            date_upload=None,
                            tags=[],
                        ),
                    ],
                ),
                Season(
                    season=3,
                    title="Staffel 3",
                    episodes=[
                        Episode(
                            season=3,
                            episode=1,
                            title="Smoke Signal",
                            url="/anime/stream/attack-on-titan/staffel-3/episode-1",
                            date_upload=None,
                            tags=[],
                        )
                    ],
                ),
                Season(
                    season=4,
                    title="Staffel 4",
                    episodes=[
                        Episode(
                            season=4,
                            episode=29,
                            title="The Final Chapter Part 1",
                            url="/anime/stream/attack-on-titan/staffel-4/episode-29",
                            date_upload=None,
                            tags=[],
                        ),
                        Episode(
                            season=4,
                            episode=30,
                            title="The Final Chapter Part 2",
                            url="/anime/stream/attack-on-titan/staffel-4/episode-30",
                            date_upload=None,
                            tags=["Series Final Episode"],
                        ),
                    ],
                ),
            ],
            movies=[
                Movie(
                    number=11,
                    title="Great need",
                    kind=MovieKind.OVA,
                    url="/anime/stream/attack-on-titan/filme/film-11",
                    date_upload=None,
                    tags=[],
                ),
                Movie(
                    number=12,
                    title="The Last Attack",
                    kind=MovieKind.MOVIE,
                    url="/anime/stream/attack-on-titan/filme/film-12",
                    date_upload=None,
                    tags=[],
                ),
            ],
        )
    )


class TestHierarchicalEndpoints:
    """Test new hierarchical API endpoints."""

    def test_get_series_detail(self, mock_anime_service, sample_series_detail_response):
        """Test GET /sources/{source}/series endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series", params={"url": "/anime/attack-on-titan"}
        )

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "series" in data
        series = data["series"]
        assert "slug" in series
        assert "seasons" in series
        assert "movies" in series

        # Check seasons
        assert len(series["seasons"]) == 3
        season_numbers = [s["season"] for s in series["seasons"]]
        assert season_numbers == [1, 3, 4]  # Should be sorted

        # Check season 4 has correct episodes
        season_4 = next(s for s in series["seasons"] if s["season"] == 4)
        assert len(season_4["episodes"]) == 2
        assert season_4["episodes"][0]["episode"] == 29
        assert season_4["episodes"][1]["episode"] == 30
        assert season_4["episodes"][1]["tags"] == ["Series Final Episode"]

        # Check movies
        assert len(series["movies"]) == 2
        movie_numbers = [m["number"] for m in series["movies"]]
        assert movie_numbers == [11, 12]  # Should be sorted

        # Check movie kinds
        movies = {m["number"]: m for m in series["movies"]}
        assert movies[11]["kind"] == "ova"
        assert movies[12]["kind"] == "movie"

    def test_get_series_seasons(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET /sources/{source}/series/seasons endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/seasons", params={"url": "/anime/attack-on-titan"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "seasons" in data
        assert len(data["seasons"]) == 3

    def test_get_specific_season(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET /sources/{source}/series/seasons/{season_num} endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/seasons/4",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "season" in data
        season = data["season"]
        assert season["season"] == 4
        assert len(season["episodes"]) == 2

    def test_get_specific_season_not_found(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET season that doesn't exist."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/seasons/99",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 404
        assert "Season 99 not found" in response.json()["detail"]

    def test_get_specific_episode(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET /sources/{source}/series/seasons/{season}/episodes/{episode} endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/seasons/4/episodes/30",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "episode" in data
        episode = data["episode"]
        assert episode["season"] == 4
        assert episode["episode"] == 30
        assert episode["title"] == "The Final Chapter Part 2"
        assert episode["tags"] == ["Series Final Episode"]

    def test_get_specific_episode_not_found(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET episode that doesn't exist."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/seasons/4/episodes/99",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 404
        assert "Episode 99 not found in season 4" in response.json()["detail"]

    def test_get_series_movies(self, mock_anime_service, sample_series_detail_response):
        """Test GET /sources/{source}/series/movies endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/movies", params={"url": "/anime/attack-on-titan"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "movies" in data
        assert len(data["movies"]) == 2

    def test_get_specific_movie(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET /sources/{source}/series/movies/{movie_num} endpoint."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/movies/12",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "movie" in data
        movie = data["movie"]
        assert movie["number"] == 12
        assert movie["title"] == "The Last Attack"
        assert movie["kind"] == "movie"

    def test_get_specific_movie_not_found(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test GET movie that doesn't exist."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series/movies/99",
            params={"url": "/anime/attack-on-titan"},
        )

        assert response.status_code == 404
        assert "Movie 99 not found" in response.json()["detail"]


class TestErrorHandling:
    """Test error handling in hierarchical endpoints."""

    def test_invalid_source(self):
        """Test invalid source handling."""
        client = TestClient(app)
        response = client.get(
            "/sources/invalid-source/series", params={"url": "/anime/test"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_missing_url_parameter(self):
        """Test missing URL parameter."""
        client = TestClient(app)
        response = client.get("/sources/aniworld/series")

        assert response.status_code == 422  # Validation error

    def test_service_exception_handling(self, mock_anime_service):
        """Test service exception handling."""
        mock_anime_service.get_series_detail.side_effect = Exception("Service error")

        client = TestClient(app)
        response = client.get("/sources/aniworld/series", params={"url": "/anime/test"})

        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestResponseFormat:
    """Test response format compliance."""

    def test_series_detail_response_schema(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test that series detail response matches expected schema."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series", params={"url": "/anime/attack-on-titan"}
        )

        assert response.status_code == 200
        data = response.json()

        # Validate top-level structure
        assert isinstance(data, dict)
        assert "series" in data

        series = data["series"]
        assert isinstance(series, dict)
        assert "slug" in series
        assert "seasons" in series
        assert "movies" in series

        # Validate seasons structure
        for season in series["seasons"]:
            assert "season" in season
            assert "title" in season
            assert "episodes" in season
            assert isinstance(season["season"], int)
            assert isinstance(season["episodes"], list)

            for episode in season["episodes"]:
                assert "season" in episode
                assert "episode" in episode
                assert "title" in episode
                assert "url" in episode
                assert "tags" in episode
                assert isinstance(episode["season"], int)
                assert isinstance(episode["episode"], int)
                assert isinstance(episode["tags"], list)

        # Validate movies structure
        for movie in series["movies"]:
            assert "number" in movie
            assert "title" in movie
            assert "kind" in movie
            assert "url" in movie
            assert "tags" in movie
            assert isinstance(movie["number"], int)
            assert movie["kind"] in ["movie", "ova", "special"]
            assert isinstance(movie["tags"], list)

    def test_content_type_json(self, mock_anime_service, sample_series_detail_response):
        """Test that responses have correct content type."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series", params={"url": "/anime/attack-on-titan"}
        )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]


class TestPerformance:
    """Test performance-related aspects."""

    def test_normalization_caching_behavior(
        self, mock_anime_service, sample_series_detail_response
    ):
        """Test that normalization doesn't cause performance issues."""
        mock_anime_service.get_series_detail.return_value = (
            sample_series_detail_response
        )

        client = TestClient(app)

        # Make multiple requests
        for _ in range(3):
            response = client.get(
                "/sources/aniworld/series", params={"url": "/anime/attack-on-titan"}
            )
            assert response.status_code == 200

        # Service should be called each time (no caching implemented yet)
        assert mock_anime_service.get_series_detail.call_count == 3

    def test_large_episode_list_handling(self, mock_anime_service):
        """Test handling of series with many episodes."""
        # Create a series with many episodes
        episodes = []
        for season in range(1, 11):  # 10 seasons
            for episode in range(1, 26):  # 25 episodes each
                episodes.append(
                    {
                        "name": f"Staffel {season} Folge {episode} : Episode {episode}",
                        "url": f"/anime/stream/long-series/staffel-{season}/episode-{episode}",
                        "date_upload": None,
                    }
                )

        large_response = DetailResponse(
            media=MediaInfo(
                name="Long Series",
                image_url="https://example.com/image.jpg",
                description="A very long series",
                episodes=episodes,
            )
        )

        mock_anime_service.get_series_detail.return_value = SeriesDetailResponse(
            series=SeriesDetail(
                slug="long-series",
                seasons=[
                    Season(
                        season=s,
                        title=f"Staffel {s}",
                        episodes=[
                            Episode(
                                season=s,
                                episode=e,
                                title=f"Episode {e}",
                                url=f"/anime/stream/long-series/staffel-{s}/episode-{e}",
                                date_upload=None,
                                tags=[],
                            )
                            for e in range(1, 26)
                        ],
                    )
                    for s in range(1, 11)
                ],
                movies=[],
            )
        )

        client = TestClient(app)
        response = client.get(
            "/sources/aniworld/series", params={"url": "/anime/long-series"}
        )

        assert response.status_code == 200
        data = response.json()

        # Should have 10 seasons
        assert len(data["series"]["seasons"]) == 10

        # Each season should have 25 episodes
        for season in data["series"]["seasons"]:
            assert len(season["episodes"]) == 25
