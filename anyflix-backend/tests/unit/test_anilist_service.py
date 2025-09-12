"""Unit tests for AniListService."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError

from lib.models.anilist import Media, MediaType, PageResponse
from lib.services.anilist_service import AniListService


class AsyncContextManagerMock:
    """Helper class for mocking async context managers in aiohttp tests."""

    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


@pytest.fixture
def anilist_service():
    """Create AniListService instance."""
    return AniListService()


@pytest.fixture
def mock_media_response():
    """Mock media response data."""
    return {
        "data": {
            "Media": {
                "id": 1,
                "title": {
                    "userPreferred": "Cowboy Bebop",
                    "romaji": "Cowboy Bebop",
                    "english": "Cowboy Bebop",
                    "native": "カウボーイビバップ",
                },
                "type": "ANIME",
                "format": "TV",
                "status": "FINISHED",
                "episodes": 26,
                "description": "In 2071, roughly fifty years after an accident with a hyperspace gateway...",
                "genres": ["Action", "Drama", "Sci-Fi"],
                "averageScore": 86,
                "popularity": 123456,
                "coverImage": {
                    "large": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1-CXtrrkMpJ8Zq.png"
                },
                "startDate": {"year": 1998, "month": 4, "day": 3},
                "endDate": {"year": 1999, "month": 4, "day": 24},
            }
        }
    }


@pytest.fixture
def mock_search_response():
    """Mock search response data."""
    return {
        "data": {
            "Page": {
                "pageInfo": {
                    "total": 100,
                    "currentPage": 1,
                    "lastPage": 5,
                    "hasNextPage": True,
                    "perPage": 20,
                },
                "media": [
                    {
                        "id": 1,
                        "title": {
                            "userPreferred": "Cowboy Bebop",
                            "romaji": "Cowboy Bebop",
                            "english": "Cowboy Bebop",
                            "native": "カウボーイビバップ",
                        },
                        "type": "ANIME",
                        "format": "TV",
                        "status": "FINISHED",
                        "episodes": 26,
                        "genres": ["Action", "Drama", "Sci-Fi"],
                        "averageScore": 86,
                        "popularity": 123456,
                        "coverImage": {
                            "large": "https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1-CXtrrkMpJ8Zq.png"
                        },
                    }
                ],
            }
        }
    }


class TestAniListService:
    """Test cases for AniListService."""

    @pytest.mark.asyncio
    async def test_init(self, anilist_service):
        """Test service initialization."""
        assert anilist_service.logger is not None
        assert anilist_service.session is None

    @pytest.mark.asyncio
    async def test_context_manager(self, anilist_service):
        """Test async context manager."""
        async with anilist_service as service:
            assert service.session is not None
        # Session should be closed after context manager exits

    @pytest.mark.asyncio
    async def test_make_request_success(self, anilist_service, mock_media_response):
        """Test successful GraphQL request."""
        # Create response mock with proper async json() but sync raise_for_status()
        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.json = AsyncMock(return_value=mock_media_response)
        mock_response.raise_for_status = Mock(return_value=None)

        # Create a proper async context manager mock
        mock_session = AsyncMock()
        # Make session.post a regular Mock (not AsyncMock) so it returns the context manager directly
        from unittest.mock import Mock

        mock_session.post = Mock(return_value=AsyncContextManagerMock(mock_response))

        anilist_service.session = mock_session

        query = "query { Media(id: 1) { id title { userPreferred } } }"
        variables = {"id": 1}

        result = await anilist_service._make_request(query, variables)

        assert result == mock_media_response["data"]
        mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_graphql_errors(self, anilist_service):
        """Test GraphQL request with errors."""
        error_response = {
            "errors": [{"message": "Variable '$id' of type 'Int' was not provided."}]
        }

        mock_response = AsyncMock()
        mock_response.json.return_value = error_response
        mock_response.raise_for_status.return_value = None

        # Create a proper async context manager mock
        mock_session = AsyncMock()
        # Make session.post a regular Mock (not AsyncMock) so it returns the context manager directly
        from unittest.mock import Mock

        mock_session.post = Mock(return_value=AsyncContextManagerMock(mock_response))

        anilist_service.session = mock_session

        query = "query { Media(id: $id) { id } }"

        with pytest.raises(ValueError, match="GraphQL errors"):
            await anilist_service._make_request(query)

    @pytest.mark.asyncio
    async def test_make_request_no_session(self, anilist_service):
        """Test request without initialized session."""
        query = "query { Media(id: 1) { id } }"

        with pytest.raises(RuntimeError, match="Service not initialized"):
            await anilist_service._make_request(query)

    @pytest.mark.asyncio
    async def test_get_media_by_id_success(self, anilist_service, mock_media_response):
        """Test successful media retrieval by ID."""
        with patch.object(
            anilist_service, "_make_request", return_value=mock_media_response["data"]
        ):
            media = await anilist_service.get_media_by_id(1)

            assert media is not None
            assert media.id == 1
            assert media.title.userPreferred == "Cowboy Bebop"
            assert media.type == MediaType.ANIME

    @pytest.mark.asyncio
    async def test_get_media_by_id_not_found(self, anilist_service):
        """Test media retrieval when media not found."""
        with patch.object(
            anilist_service, "_make_request", return_value={"Media": None}
        ):
            media = await anilist_service.get_media_by_id(999999)

            assert media is None

    @pytest.mark.asyncio
    async def test_search_media_success(self, anilist_service, mock_search_response):
        """Test successful media search."""
        with patch.object(
            anilist_service, "_make_request", return_value=mock_search_response["data"]
        ):
            result = await anilist_service.search_media("Cowboy Bebop", MediaType.ANIME)

            assert result is not None
            assert isinstance(result, PageResponse)
            assert result.pageInfo.total == 100
            assert len(result.media) == 1
            assert result.media[0].title.userPreferred == "Cowboy Bebop"

    @pytest.mark.asyncio
    async def test_search_media_no_results(self, anilist_service):
        """Test media search with no results."""
        with patch.object(
            anilist_service, "_make_request", return_value={"Page": None}
        ):
            result = await anilist_service.search_media("NonexistentAnime")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_trending_anime(self, anilist_service, mock_search_response):
        """Test getting trending anime."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.get_trending_anime()

            mock_search.assert_called_once_with(
                media_type=MediaType.ANIME,
                page=1,
                per_page=20,
                sort=["TRENDING_DESC", "POPULARITY_DESC"],
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_popular_anime(self, anilist_service, mock_search_response):
        """Test getting popular anime."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.get_popular_anime()

            mock_search.assert_called_once_with(
                media_type=MediaType.ANIME,
                page=1,
                per_page=20,
                sort=["POPULARITY_DESC"],
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_top_rated_anime(self, anilist_service, mock_search_response):
        """Test getting top rated anime."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.get_top_rated_anime()

            mock_search.assert_called_once_with(
                media_type=MediaType.ANIME, page=1, per_page=20, sort=["SCORE_DESC"]
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_seasonal_anime(self, anilist_service, mock_search_response):
        """Test getting seasonal anime."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.get_seasonal_anime("FALL", 2023)

            mock_search.assert_called_once_with(
                media_type=MediaType.ANIME,
                season="FALL",
                seasonYear=2023,
                page=1,
                per_page=20,
                sort=["POPULARITY_DESC"],
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_upcoming_anime(self, anilist_service, mock_search_response):
        """Test getting upcoming anime."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.get_upcoming_anime()

            mock_search.assert_called_once_with(
                media_type=MediaType.ANIME,
                status="NOT_YET_RELEASED",
                page=1,
                per_page=20,
                sort=["POPULARITY_DESC"],
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_search_anime(self, anilist_service, mock_search_response):
        """Test anime search."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.search_anime("Attack on Titan")

            mock_search.assert_called_once_with(
                search="Attack on Titan",
                media_type=MediaType.ANIME,
                page=1,
                per_page=20,
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_search_manga(self, anilist_service, mock_search_response):
        """Test manga search."""
        with patch.object(
            anilist_service,
            "search_media",
            return_value=mock_search_response["data"]["Page"],
        ) as mock_search:
            result = await anilist_service.search_manga("One Piece")

            mock_search.assert_called_once_with(
                search="One Piece", media_type=MediaType.MANGA, page=1, per_page=20
            )
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_media_relations(self, anilist_service, mock_media_response):
        """Test getting media with relations."""
        with patch.object(
            anilist_service,
            "get_media_by_id",
            return_value=mock_media_response["data"]["Media"],
        ) as mock_get:
            result = await anilist_service.get_media_relations(1)

            mock_get.assert_called_once_with(1, detailed=True)
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_media_characters(self, anilist_service, mock_media_response):
        """Test getting media with characters."""
        with patch.object(
            anilist_service,
            "get_media_by_id",
            return_value=mock_media_response["data"]["Media"],
        ) as mock_get:
            result = await anilist_service.get_media_characters(1)

            mock_get.assert_called_once_with(1, detailed=True)
            assert result is not None

    @pytest.mark.asyncio
    async def test_get_media_staff(self, anilist_service, mock_media_response):
        """Test getting media with staff."""
        with patch.object(
            anilist_service,
            "get_media_by_id",
            return_value=mock_media_response["data"]["Media"],
        ) as mock_get:
            result = await anilist_service.get_media_staff(1)

            mock_get.assert_called_once_with(1, detailed=True)
            assert result is not None

    @pytest.mark.asyncio
    async def test_http_error_handling(self, anilist_service):
        """Test HTTP error handling."""
        # Create response mock that raises ClientError on raise_for_status()
        from unittest.mock import Mock

        mock_response = Mock()
        mock_response.json = AsyncMock()  # Won't be called due to exception
        mock_response.raise_for_status = Mock(side_effect=ClientError("HTTP 500"))

        # Create a proper async context manager mock
        mock_session = AsyncMock()
        # Make session.post a regular Mock (not AsyncMock) so it returns the context manager directly
        from unittest.mock import Mock

        mock_session.post = Mock(return_value=AsyncContextManagerMock(mock_response))

        anilist_service.session = mock_session

        query = "query { Media(id: 1) { id } }"

        with pytest.raises(ClientError):
            await anilist_service._make_request(query)

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, anilist_service):
        """Test validation error handling in get_media_by_id."""
        invalid_response = {
            "Media": {
                "id": "invalid_id",  # Should be int
                "title": "Missing required fields",
            }
        }

        with patch.object(
            anilist_service, "_make_request", return_value=invalid_response
        ):
            with pytest.raises(Exception):  # ValidationError or similar
                await anilist_service.get_media_by_id(1)
