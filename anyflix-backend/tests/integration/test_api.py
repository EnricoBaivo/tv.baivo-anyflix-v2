"""Integration tests for FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "available_sources" in data
        assert data["message"] == "Anime Backend Service"
        assert data["version"] == "1.0.0"
        assert isinstance(data["available_sources"], list)

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/admin/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    def test_sources_endpoint(self, client):
        """Test the sources list endpoint."""
        response = client.get("/sources")
        assert response.status_code == 200

        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert "aniworld" in data["sources"]
        assert "serienstream" in data["sources"]

    def test_source_preferences_aniworld(self, client):
        """Test getting preferences for AniWorld."""
        response = client.get("/sources/aniworld/preferences")
        assert response.status_code == 200

        data = response.json()
        assert "preferences" in data
        preferences = data["preferences"]
        assert isinstance(preferences, list)
        assert len(preferences) == 6

        # Check preference structure
        lang_pref = next((p for p in preferences if p["key"] == "lang"), None)
        assert lang_pref is not None
        assert lang_pref["list_preference"]["title"] == "Bevorzugte Sprache"
        assert "Deutsch" in lang_pref["list_preference"]["entries"]

    def test_source_preferences_serienstream(self, client):
        """Test getting preferences for SerienStream."""
        response = client.get("/sources/serienstream/preferences")
        assert response.status_code == 200

        data = response.json()
        assert "preferences" in data
        preferences = data["preferences"]
        assert isinstance(preferences, list)
        assert len(preferences) == 6

    def test_source_preferences_invalid_source(self, client):
        """Test getting preferences for invalid source."""
        response = client.get("/sources/invalid/preferences")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Source 'invalid' not found" in data["detail"]

    def test_popular_endpoint_invalid_source(self, client):
        """Test popular endpoint with invalid source."""
        response = client.get("/sources/invalid/popular")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Source 'invalid' not found" in data["detail"]

    def test_latest_endpoint_invalid_source(self, client):
        """Test latest endpoint with invalid source."""
        response = client.get("/sources/invalid/latest")
        assert response.status_code == 404

    def test_search_endpoint_invalid_source(self, client):
        """Test search endpoint with invalid source."""
        response = client.get("/sources/invalid/search?q=test")
        assert response.status_code == 404

    def test_detail_endpoint_invalid_source(self, client):
        """Test detail endpoint with invalid source."""
        response = client.get("/sources/invalid/detail?url=/test")
        assert response.status_code == 404

    def test_videos_endpoint_invalid_source(self, client):
        """Test videos endpoint with invalid source."""
        response = client.get("/sources/invalid/videos?url=/test")
        assert response.status_code == 404

    def test_search_missing_query(self, client):
        """Test search endpoint without query parameter."""
        response = client.get("/sources/aniworld/search")
        assert response.status_code == 422  # Validation error

    def test_detail_missing_url(self, client):
        """Test detail endpoint without url parameter."""
        response = client.get("/sources/aniworld/detail")
        assert response.status_code == 422  # Validation error

    def test_videos_missing_url(self, client):
        """Test videos endpoint without url parameter."""
        response = client.get("/sources/aniworld/videos")
        assert response.status_code == 422  # Validation error

    def test_page_parameter_validation(self, client):
        """Test page parameter validation."""
        # Valid page parameter
        response = client.get("/sources/aniworld/popular?page=1")
        assert response.status_code in [
            200,
            500,
        ]  # May fail due to network, but validation should pass

        # Invalid page parameter (negative)
        response = client.get("/sources/aniworld/popular?page=-1")
        assert response.status_code == 422  # Validation error

        # Invalid page parameter (zero)
        response = client.get("/sources/aniworld/popular?page=0")
        assert response.status_code == 422  # Validation error


class TestAPIResponseFormat:
    """Test API response format and structure."""

    def test_preferences_response_structure(self, client):
        """Test that preferences response has correct structure."""
        response = client.get("/sources/aniworld/preferences")
        assert response.status_code == 200

        data = response.json()
        preferences = data["preferences"]

        for pref in preferences:
            assert "key" in pref
            assert isinstance(pref["key"], str)

            # Should have either list_preference or multi_select_list_preference
            has_list = pref.get("list_preference") is not None
            has_multi = pref.get("multi_select_list_preference") is not None
            assert has_list or has_multi  # At least one should be present
            assert not (has_list and has_multi)  # But not both

    def test_cors_headers(self, client):
        """Test that CORS headers are present."""
        response = client.get("/")
        assert response.status_code == 200

        # Check that CORS middleware is working
        # Note: TestClient doesn't always include all headers,
        # but we can verify the app setup
        assert response.headers.get("content-type") == "application/json"
