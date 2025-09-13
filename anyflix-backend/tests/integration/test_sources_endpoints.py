"""Integration tests for all sources API endpoints."""

import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Test data storage for documentation updates
test_results: Dict[str, Dict[str, Any]] = {}


class TestSourcesEndpoints:
    """Integration tests for all sources API endpoints with real response capture."""

    def setup_method(self):
        """Set up test method."""
        self.test_source = "aniworld"  # Primary test source
        self.backup_source = "serienstream"  # Backup if primary fails

    def capture_response(
        self, endpoint: str, response_data: Dict[str, Any], status_code: int = 200
    ):
        """Capture response data for documentation updates."""
        test_results[endpoint] = {
            "status_code": status_code,
            "response": response_data,
            "response_size": (
                len(json.dumps(response_data)) if isinstance(response_data, dict) else 0
            ),
        }

    def test_01_get_sources(self):
        """Test GET /sources/ - List Available Sources"""
        response = client.get("/sources/")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0

        self.capture_response("GET /sources/", data)
        print(f"✅ Sources available: {data['sources']}")

    def test_02_get_source_preferences(self):
        """Test GET /sources/{source}/preferences - Get Source Configuration"""
        response = client.get(f"/sources/{self.test_source}/preferences")

        assert response.status_code == 200
        data = response.json()
        assert "preferences" in data

        self.capture_response(f"GET /sources/{self.test_source}/preferences", data)
        print(
            f"✅ Source preferences retrieved: {len(data.get('preferences', []))} items"
        )

    def test_03_get_popular_content(self):
        """Test GET /sources/{source}/popular - Get Popular Content"""
        response = client.get(f"/sources/{self.test_source}/popular?page=1")

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "list" in data
        assert "has_next_page" in data
        assert isinstance(data["list"], list)

        self.capture_response(f"GET /sources/{self.test_source}/popular", data)
        print(f"✅ Popular content retrieved: {len(data['list'])} items")

        # Test with pagination
        if data.get("has_next_page"):
            page2_response = client.get(f"/sources/{self.test_source}/popular?page=2")
            assert page2_response.status_code == 200
            print("✅ Pagination works correctly")

    def test_04_get_latest_updates(self):
        """Test GET /sources/{source}/latest - Get Latest Updates"""
        response = client.get(f"/sources/{self.test_source}/latest?page=1")

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "list" in data
        assert "has_next_page" in data
        assert isinstance(data["list"], list)

        self.capture_response(f"GET /sources/{self.test_source}/latest", data)
        print(f"✅ Latest updates retrieved: {len(data['list'])} items")

    def test_05_search_content(self):
        """Test GET /sources/{source}/search - Search Content"""
        search_queries = ["attack", "demon", "naruto"]  # Common anime terms

        for query in search_queries:
            response = client.get(
                f"/sources/{self.test_source}/search?q={query}&page=1"
            )

            if response.status_code == 200:
                data = response.json()
                assert "type" in data
                assert "list" in data
                assert "has_next_page" in data
                assert isinstance(data["list"], list)

                self.capture_response(f"GET /sources/{self.test_source}/search", data)
                print(f"✅ Search '{query}' successful: {len(data['list'])} results")

                # Use first successful search result for subsequent tests
                if data["list"]:
                    self.test_series_url = data["list"][0]["link"]
                    print(
                        f"📝 Using series URL for further tests: {self.test_series_url}"
                    )
                break
        else:
            pytest.skip("No successful search results found")

    def test_06_get_series_detail(self):
        """Test GET /sources/{source}/series - Get Full Series Data"""
        if not hasattr(self, "test_series_url"):
            pytest.skip("No series URL available from search test")

        response = client.get(
            f"/sources/{self.test_source}/series?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "series" in data
        assert "slug" in data["series"]

        self.capture_response(f"GET /sources/{self.test_source}/series", data)

        # Store series data for subsequent tests
        self.series_data = data
        print(f"✅ Series detail retrieved: {data['series']['slug']}")
        print(f"   Seasons: {len(data['series'].get('seasons', []))}")
        print(f"   Movies: {len(data['series'].get('movies', []))}")

    def test_07_get_series_seasons(self):
        """Test GET /sources/{source}/series/seasons - Get All Seasons"""
        if not hasattr(self, "test_series_url"):
            pytest.skip("No series URL available")

        response = client.get(
            f"/sources/{self.test_source}/series/seasons?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "seasons" in data
        assert isinstance(data["seasons"], list)

        self.capture_response(f"GET /sources/{self.test_source}/series/seasons", data)
        print(f"✅ Seasons retrieved: {len(data['seasons'])} seasons")

    def test_08_get_specific_season(self):
        """Test GET /sources/{source}/series/seasons/{season_num} - Get Specific Season"""
        if not hasattr(self, "series_data") or not self.series_data["series"].get(
            "seasons"
        ):
            pytest.skip("No seasons available")

        season_num = self.series_data["series"]["seasons"][0]["season"]
        response = client.get(
            f"/sources/{self.test_source}/series/seasons/{season_num}?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "season" in data
        assert data["season"]["season"] == season_num

        self.capture_response(
            f"GET /sources/{self.test_source}/series/seasons/{season_num}", data
        )
        print(
            f"✅ Season {season_num} retrieved: {len(data['season'].get('episodes', []))} episodes"
        )

    def test_09_get_specific_episode(self):
        """Test GET /sources/{source}/series/seasons/{season_num}/episodes/{episode_num} - Get Specific Episode"""
        if not hasattr(self, "series_data") or not self.series_data["series"].get(
            "seasons"
        ):
            pytest.skip("No seasons available")

        season = self.series_data["series"]["seasons"][0]
        if not season.get("episodes"):
            pytest.skip("No episodes available")

        season_num = season["season"]
        episode_num = season["episodes"][0]["episode"]

        response = client.get(
            f"/sources/{self.test_source}/series/seasons/{season_num}/episodes/{episode_num}?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "episode" in data
        assert data["episode"]["season"] == season_num
        assert data["episode"]["episode"] == episode_num

        self.capture_response(
            f"GET /sources/{self.test_source}/series/seasons/{season_num}/episodes/{episode_num}",
            data,
        )

        # Store episode URL for video sources test
        self.episode_url = data["episode"]["url"]
        print(
            f"✅ Episode S{season_num}E{episode_num} retrieved: {data['episode']['title']}"
        )

    def test_10_get_series_movies(self):
        """Test GET /sources/{source}/series/movies - Get All Movies/OVAs"""
        if not hasattr(self, "test_series_url"):
            pytest.skip("No series URL available")

        response = client.get(
            f"/sources/{self.test_source}/series/movies?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "movies" in data
        assert isinstance(data["movies"], list)

        self.capture_response(f"GET /sources/{self.test_source}/series/movies", data)
        print(f"✅ Movies retrieved: {len(data['movies'])} movies/OVAs")

    def test_11_get_specific_movie(self):
        """Test GET /sources/{source}/series/movies/{movie_num} - Get Specific Movie/OVA"""
        if not hasattr(self, "series_data") or not self.series_data["series"].get(
            "movies"
        ):
            pytest.skip("No movies available")

        movie_num = self.series_data["series"]["movies"][0]["number"]
        response = client.get(
            f"/sources/{self.test_source}/series/movies/{movie_num}?url={self.test_series_url}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "type" in data
        assert "movie" in data
        assert data["movie"]["number"] == movie_num

        self.capture_response(
            f"GET /sources/{self.test_source}/series/movies/{movie_num}", data
        )
        print(f"✅ Movie {movie_num} retrieved: {data['movie']['title']}")

    def test_12_get_video_sources(self):
        """Test GET /sources/{source}/videos - Get Video Streaming Links"""
        if not hasattr(self, "episode_url"):
            pytest.skip("No episode URL available")

        response = client.get(
            f"/sources/{self.test_source}/videos?url={self.episode_url}"
        )

        # This might fail due to external dependencies, so we handle both cases
        if response.status_code == 200:
            data = response.json()
            assert "type" in data
            assert "videos" in data
            assert isinstance(data["videos"], list)

            self.capture_response(f"GET /sources/{self.test_source}/videos", data)
            print(f"✅ Video sources retrieved: {len(data['videos'])} sources")
        else:
            # Capture error response for documentation
            error_data = (
                response.json()
                if response.headers.get("content-type") == "application/json"
                else {"error": "Non-JSON error response"}
            )
            self.capture_response(
                f"GET /sources/{self.test_source}/videos",
                error_data,
                response.status_code,
            )
            print(f"⚠️ Video sources failed (expected): {response.status_code}")

    def test_13_extract_trailer_url(self):
        """Test POST /sources/trailer - Extract Streamable Trailer URL"""
        # Test with AniList trailer data
        anilist_trailer_data = {
            "anilist_trailer": {"id": "PfuNSVDqPiks", "site": "youtube"}
        }

        response = client.post("/sources/trailer", json=anilist_trailer_data)

        # This might fail due to external dependencies
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "original_url" in data

            self.capture_response("POST /sources/trailer", data)
            print(f"✅ Trailer extraction successful: {data.get('success')}")
        else:
            error_data = (
                response.json()
                if response.headers.get("content-type") == "application/json"
                else {"error": "Non-JSON error response"}
            )
            self.capture_response(
                "POST /sources/trailer", error_data, response.status_code
            )
            print(f"⚠️ Trailer extraction failed (expected): {response.status_code}")

    def test_14_error_handling(self):
        """Test error handling for invalid requests"""
        # Test invalid source
        response = client.get("/sources/invalid_source/popular")
        assert response.status_code == 404

        # Test missing required parameters
        response = client.get(
            f"/sources/{self.test_source}/search"
        )  # Missing 'q' parameter
        assert response.status_code == 422

        # Test invalid season/episode numbers
        response = client.get(
            f"/sources/{self.test_source}/series/seasons/999/episodes/999?url=test"
        )
        assert response.status_code == 404

        print("✅ Error handling tests passed")

    @classmethod
    def teardown_class(cls):
        """Save test results for documentation updates."""
        with open("tests/integration/test_results.json", "w") as f:
            json.dump(test_results, f, indent=2, default=str)

        print(f"\n📊 Test Results Summary:")
        print(f"   Total endpoints tested: {len(test_results)}")
        successful = len([r for r in test_results.values() if r["status_code"] == 200])
        print(f"   Successful responses: {successful}")
        print(f"   Test results saved to: tests/integration/test_results.json")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
