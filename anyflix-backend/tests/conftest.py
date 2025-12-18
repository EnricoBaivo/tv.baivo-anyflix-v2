"""Pytest configuration and shared fixtures."""

import os

import pytest
import pytest_asyncio
from aiocache import caches
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app

# Force memory cache for tests to avoid Redis event loop issues
# This must be done before any cache operations


def initialize_test_cache():
    """Initialize a memory-based cache for testing.

    Uses SimpleMemoryCache instead of Redis to avoid event loop issues
    when running tests with pytest-asyncio.
    """
    from lib.utils.caching import PydanticSerializer

    test_cache_config = {
        "default": {
            "cache": "aiocache.SimpleMemoryCache",
            "serializer": {"class": PydanticSerializer},
        }
    }
    caches.set_config(test_cache_config)


# Initialize test cache at module load time
initialize_test_cache()

# Also set environment variable to disable Redis caching in app config
os.environ.setdefault("ENABLE_CACHING", "false")


@pytest.fixture
def client():
    """Create a synchronous test client for FastAPI."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client():
    """Create an async test client for FastAPI."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# Test data URLs for AniWorld provider
@pytest.fixture
def aniworld_test_data():
    """Return test data for AniWorld provider."""
    return {
        "source": "aniworld",
        "base_url": "https://aniworld.to",
        "series_url": "https://aniworld.to/anime/stream/one-punch-man",
        "series_slug": "one-punch-man",
        "season_url": "https://aniworld.to/anime/stream/one-punch-man/staffel-1",
        "episode_url": "https://aniworld.to/anime/stream/one-punch-man/staffel-1/episode-1",
        "movies_url": "https://aniworld.to/anime/stream/one-punch-man/filme",
        "search_query": "one punch",
        "expected_type": "anime",
        "season_num": 1,
        "episode_num": 1,
    }


# Test data URLs for SerienStream provider
@pytest.fixture
def serienstream_test_data():
    """Return test data for SerienStream provider."""
    return {
        "source": "serienstream",
        "base_url": "https://serienstream.to",
        "series_url": "https://serienstream.to/serie/stream/the-witcher",
        "series_slug": "the-witcher",
        "season_url": "https://serienstream.to/serie/stream/the-witcher/staffel-1",
        "episode_url": "https://serienstream.to/serie/stream/the-witcher/staffel-1/episode-1",
        "movies_url": "https://serienstream.to/serie/stream/the-witcher/filme",
        "search_query": "witcher",
        "expected_type": "normal",
        "season_num": 1,
        "episode_num": 1,
    }


# Combined fixture for parametrized tests
@pytest.fixture(params=["aniworld", "serienstream"])
def provider_test_data(request, aniworld_test_data, serienstream_test_data):
    """Return test data for the specified provider."""
    if request.param == "aniworld":
        return aniworld_test_data
    return serienstream_test_data
