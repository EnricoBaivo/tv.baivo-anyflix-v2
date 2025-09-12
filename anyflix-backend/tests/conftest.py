"""Pytest configuration and fixtures."""

import pytest

from lib.providers.aniworld import AniWorldProvider
from lib.providers.serienstream import SerienStreamProvider
from lib.services.media_service import MediaService


@pytest.fixture
def anime_service():
    """Create a MediaService instance for testing (backward compatibility)."""
    return MediaService()


@pytest.fixture
def media_service():
    """Create a MediaService instance for testing."""
    return MediaService()


@pytest.fixture
def aniworld_provider():
    """Create an AniWorldProvider instance for testing."""
    return AniWorldProvider()


@pytest.fixture
def serienstream_provider():
    """Create a SerienStreamProvider instance for testing."""
    return SerienStreamProvider()


@pytest.fixture
def sample_preferences():
    """Sample preferences data for testing."""
    return [
        {
            "key": "lang",
            "title": "Bevorzugte Sprache",
            "entries": ["Deutsch", "Englisch"],
            "values": ["Deutscher", "Englischer"],
        },
        {
            "key": "type",
            "title": "Bevorzugter Typ",
            "entries": ["Dub", "Sub"],
            "values": ["Dub", "Sub"],
        },
    ]
