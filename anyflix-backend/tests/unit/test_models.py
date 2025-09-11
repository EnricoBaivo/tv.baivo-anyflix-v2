"""Unit tests for data models."""

import pytest
from pydantic import ValidationError

from lib.models.base import (
    AnimeInfo,
    AnimeSource,
    Episode,
    SearchResult,
    SourcePreference,
    VideoSource,
)
from lib.models.responses import (
    DetailResponse,
    LatestResponse,
    PopularResponse,
    SearchResponse,
    VideoListResponse,
)


class TestBaseModels:
    """Test cases for base models."""

    def test_anime_source_creation(self):
        """Test AnimeSource model creation."""
        source = AnimeSource(
            name="Test Source",
            lang="en",
            base_url="https://test.com",
            version="1.0.0",
            pkg_path="test/path",
        )
        assert source.name == "Test Source"
        assert source.lang == "en"
        assert source.base_url == "https://test.com"
        assert source.api_url == ""  # Default value
        assert source.is_nsfw is False  # Default value

    def test_anime_info_creation(self):
        """Test AnimeInfo model creation."""
        episodes = [
            {"name": "Episode 1", "url": "/ep1", "date_upload": None},
            {"name": "Episode 2", "url": "/ep2", "date_upload": None},
        ]

        anime = AnimeInfo(
            name="Test Anime",
            image_url="https://test.com/image.jpg",
            description="Test description",
            episodes=episodes,
            genre=["Action", "Adventure"],
        )

        assert anime.name == "Test Anime"
        assert anime.image_url == "https://test.com/image.jpg"
        assert len(anime.episodes) == 2
        assert len(anime.genre) == 2
        assert anime.status == 5  # Default value
        assert anime.author == ""  # Default value

    def test_search_result_creation(self):
        """Test SearchResult model creation."""
        result = SearchResult(
            name="Test Result",
            image_url="https://test.com/image.jpg",
            link="/test/link",
        )
        assert result.name == "Test Result"
        assert result.image_url == "https://test.com/image.jpg"
        assert result.link == "/test/link"

    def test_video_source_creation(self):
        """Test VideoSource model creation."""
        video = VideoSource(
            url="https://video.com/stream",
            original_url="https://video.com/stream",
            quality="1080p",
        )
        assert video.url == "https://video.com/stream"
        assert video.quality == "1080p"
        assert video.headers is None  # Optional field
        assert video.subtitles is None  # Optional field

    def test_source_preference_creation(self):
        """Test SourcePreference model creation."""
        # Test list preference
        list_pref = SourcePreference(
            key="test_key",
            list_preference={
                "title": "Test Preference",
                "entries": ["Option 1", "Option 2"],
                "entryValues": ["opt1", "opt2"],
            },
        )
        assert list_pref.key == "test_key"
        assert list_pref.list_preference["title"] == "Test Preference"
        assert list_pref.multi_select_list_preference is None

        # Test multi-select preference
        multi_pref = SourcePreference(
            key="multi_key",
            multi_select_list_preference={
                "title": "Multi Select",
                "entries": ["A", "B", "C"],
                "values": ["A", "B"],
            },
        )
        assert multi_pref.key == "multi_key"
        assert multi_pref.multi_select_list_preference["title"] == "Multi Select"
        assert multi_pref.list_preference is None


class TestResponseModels:
    """Test cases for response models."""

    def test_popular_response(self):
        """Test PopularResponse model."""
        results = [
            SearchResult(name="Anime 1", image_url="img1.jpg", link="/anime1"),
            SearchResult(name="Anime 2", image_url="img2.jpg", link="/anime2"),
        ]

        response = PopularResponse(list=results, has_next_page=True)
        assert len(response.list) == 2
        assert response.has_next_page is True

        # Test default value
        response_default = PopularResponse(list=results)
        assert response_default.has_next_page is False

    def test_latest_response(self):
        """Test LatestResponse model."""
        results = [SearchResult(name="Latest", image_url="img.jpg", link="/latest")]
        response = LatestResponse(list=results)
        assert len(response.list) == 1
        assert response.has_next_page is False

    def test_search_response(self):
        """Test SearchResponse model."""
        results = [
            SearchResult(name="Search Result", image_url="img.jpg", link="/search")
        ]
        response = SearchResponse(list=results)
        assert len(response.list) == 1
        assert response.has_next_page is False

    def test_detail_response(self):
        """Test DetailResponse model."""
        anime = AnimeInfo(
            name="Detail Anime",
            image_url="detail.jpg",
            description="Detailed description",
        )
        response = DetailResponse(anime=anime)
        assert response.anime.name == "Detail Anime"

    def test_video_list_response(self):
        """Test VideoListResponse model."""
        videos = [
            VideoSource(url="video1.mp4", original_url="video1.mp4", quality="720p"),
            VideoSource(url="video2.mp4", original_url="video2.mp4", quality="1080p"),
        ]
        response = VideoListResponse(videos=videos)
        assert len(response.videos) == 2
        assert response.videos[0].quality == "720p"
        assert response.videos[1].quality == "1080p"


class TestModelValidation:
    """Test model validation and error handling."""

    def test_anime_source_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            AnimeSource()  # Missing required fields

        with pytest.raises(ValidationError):
            AnimeSource(name="Test")  # Missing other required fields

    def test_episode_creation(self):
        """Test new Episode model creation with required fields."""
        episode = Episode(
            season=1, episode=5, title="Test Episode", url="/test/episode"
        )
        assert episode.season == 1
        assert episode.episode == 5
        assert episode.title == "Test Episode"
        assert episode.url == "/test/episode"
        assert episode.date_upload is None  # Optional field
        assert episode.tags == []  # Default empty list

        # Test with optional fields
        episode_with_extras = Episode(
            season=2,
            episode=10,
            title="Test Episode 2",
            url="/test/episode2",
            date_upload="1640995200000",
            tags=["action", "drama"],
        )
        assert episode_with_extras.date_upload == "1640995200000"
        assert episode_with_extras.tags == ["action", "drama"]

    def test_episode_required_fields(self):
        """Test Episode required fields validation."""
        with pytest.raises(ValidationError):
            Episode()  # Missing all required fields

        with pytest.raises(ValidationError):
            Episode(season=1)  # Missing episode, title, url

        with pytest.raises(ValidationError):
            Episode(season=1, episode=1)  # Missing title, url

        with pytest.raises(ValidationError):
            Episode(season=1, episode=1, title="Test")  # Missing url

    def test_search_result_validation(self):
        """Test SearchResult validation."""
        # Valid creation
        result = SearchResult(
            name="Valid", image_url="https://example.com/image.jpg", link="/valid"
        )
        assert result.name == "Valid"

        # Invalid - missing required fields
        with pytest.raises(ValidationError):
            SearchResult(name="Invalid")  # Missing image_url and link
