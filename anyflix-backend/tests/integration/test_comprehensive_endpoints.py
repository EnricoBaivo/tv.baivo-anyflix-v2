"""Comprehensive integration tests with better error handling and more endpoints."""

import json
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestComprehensiveEndpoints:
    """Comprehensive tests that handle external service failures gracefully."""

    def setup_method(self):
        """Set up test method."""
        self.test_source = "aniworld"
        self.test_results = {}

    def capture_response(
        self, endpoint: str, response_data: Any, status_code: int = 200
    ):
        """Capture response for documentation."""
        self.test_results[endpoint] = {
            "status_code": status_code,
            "response": response_data,
            "response_size": (
                len(json.dumps(response_data, default=str)) if response_data else 0
            ),
        }

    def test_basic_endpoints(self):
        """Test basic endpoints that don't depend on external services."""

        # Test sources list
        response = client.get("/sources/")
        assert response.status_code == 200
        data = response.json()
        self.capture_response("GET /sources/", data)

        # Test source preferences
        response = client.get(f"/sources/{self.test_source}/preferences")
        assert response.status_code == 200
        data = response.json()
        self.capture_response(f"GET /sources/{self.test_source}/preferences", data)

        print("✅ Basic endpoints tested successfully")

    def test_content_discovery_endpoints(self):
        """Test content discovery endpoints."""

        endpoints = ["popular", "latest"]

        for endpoint in endpoints:
            response = client.get(f"/sources/{self.test_source}/{endpoint}?page=1")

            if response.status_code == 200:
                data = response.json()
                self.capture_response(
                    f"GET /sources/{self.test_source}/{endpoint}", data
                )
                print(
                    f"✅ {endpoint} endpoint successful: {len(data.get('list', []))} items"
                )

                # Store first item for series testing
                if not hasattr(self, "test_series_url") and data.get("list"):
                    self.test_series_url = data["list"][0]["link"]
                    self.test_series_name = data["list"][0]["name"]
                    print(f"📝 Selected series for testing: {self.test_series_name}")
            else:
                error_data = {"error": f"Failed with status {response.status_code}"}
                self.capture_response(
                    f"GET /sources/{self.test_source}/{endpoint}",
                    error_data,
                    response.status_code,
                )
                print(f"⚠️ {endpoint} endpoint failed: {response.status_code}")

    def test_search_endpoint(self):
        """Test search endpoint with multiple queries."""

        search_terms = ["attack", "demon", "one piece", "naruto"]

        for term in search_terms:
            response = client.get(f"/sources/{self.test_source}/search?q={term}&page=1")

            if response.status_code == 200:
                data = response.json()

                if data.get("list"):
                    self.capture_response(
                        f"GET /sources/{self.test_source}/search", data
                    )
                    print(f"✅ Search '{term}' successful: {len(data['list'])} results")

                    # Store a good series URL for further testing
                    if not hasattr(self, "test_series_url"):
                        self.test_series_url = data["list"][0]["link"]
                        self.test_series_name = data["list"][0]["name"]
                        print(f"📝 Using '{self.test_series_name}' for series tests")

                    break
        else:
            print("⚠️ No successful search results found")

    def test_series_endpoints(self):
        """Test series-related endpoints if we have a valid series URL."""

        if not hasattr(self, "test_series_url"):
            print("⚠️ No series URL available, skipping series tests")
            return

        # Test series detail
        try:
            response = client.get(
                f"/sources/{self.test_source}/series?url={self.test_series_url}"
            )

            if response.status_code == 200:
                data = response.json()
                self.capture_response(f"GET /sources/{self.test_source}/series", data)
                print(f"✅ Series detail retrieved for: {self.test_series_name}")

                # Store series data for sub-endpoint tests
                self.series_data = data

                # Test seasons endpoint
                seasons_response = client.get(
                    f"/sources/{self.test_source}/series/seasons?url={self.test_series_url}"
                )
                if seasons_response.status_code == 200:
                    seasons_data = seasons_response.json()
                    self.capture_response(
                        f"GET /sources/{self.test_source}/series/seasons", seasons_data
                    )
                    print(
                        f"✅ Seasons retrieved: {len(seasons_data.get('seasons', []))} seasons"
                    )

                # Test movies endpoint
                movies_response = client.get(
                    f"/sources/{self.test_source}/series/movies?url={self.test_series_url}"
                )
                if movies_response.status_code == 200:
                    movies_data = movies_response.json()
                    self.capture_response(
                        f"GET /sources/{self.test_source}/series/movies", movies_data
                    )
                    print(
                        f"✅ Movies retrieved: {len(movies_data.get('movies', []))} movies"
                    )

                # Test specific season if available
                if data.get("series", {}).get("seasons"):
                    season_num = data["series"]["seasons"][0]["season"]
                    season_response = client.get(
                        f"/sources/{self.test_source}/series/seasons/{season_num}?url={self.test_series_url}"
                    )
                    if season_response.status_code == 200:
                        season_data = season_response.json()
                        self.capture_response(
                            f"GET /sources/{self.test_source}/series/seasons/{season_num}",
                            season_data,
                        )
                        print(f"✅ Season {season_num} retrieved")

                        # Test specific episode if available
                        if season_data.get("season", {}).get("episodes"):
                            episode_num = season_data["season"]["episodes"][0][
                                "episode"
                            ]
                            episode_response = client.get(
                                f"/sources/{self.test_source}/series/seasons/{season_num}/episodes/{episode_num}?url={self.test_series_url}"
                            )
                            if episode_response.status_code == 200:
                                episode_data = episode_response.json()
                                self.capture_response(
                                    f"GET /sources/{self.test_source}/series/seasons/{season_num}/episodes/{episode_num}",
                                    episode_data,
                                )
                                print(
                                    f"✅ Episode S{season_num}E{episode_num} retrieved"
                                )

                                # Store episode URL for video test
                                self.episode_url = episode_data["episode"]["url"]

                # Test specific movie if available
                if data.get("series", {}).get("movies"):
                    movie_num = data["series"]["movies"][0]["number"]
                    movie_response = client.get(
                        f"/sources/{self.test_source}/series/movies/{movie_num}?url={self.test_series_url}"
                    )
                    if movie_response.status_code == 200:
                        movie_data = movie_response.json()
                        self.capture_response(
                            f"GET /sources/{self.test_source}/series/movies/{movie_num}",
                            movie_data,
                        )
                        print(f"✅ Movie {movie_num} retrieved")

            else:
                error_data = {
                    "error": f"Series detail failed with status {response.status_code}"
                }
                self.capture_response(
                    f"GET /sources/{self.test_source}/series",
                    error_data,
                    response.status_code,
                )
                print(f"⚠️ Series detail failed: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Series endpoints test failed: {e}")

    def test_video_endpoint(self):
        """Test video sources endpoint if we have an episode URL."""

        if not hasattr(self, "episode_url"):
            print("⚠️ No episode URL available, skipping video test")
            return

        try:
            response = client.get(
                f"/sources/{self.test_source}/videos?url={self.episode_url}"
            )

            if response.status_code == 200:
                data = response.json()
                self.capture_response(f"GET /sources/{self.test_source}/videos", data)
                print(
                    f"✅ Video sources retrieved: {len(data.get('videos', []))} sources"
                )
            else:
                error_data = {
                    "error": f"Video sources failed with status {response.status_code}"
                }
                self.capture_response(
                    f"GET /sources/{self.test_source}/videos",
                    error_data,
                    response.status_code,
                )
                print(f"⚠️ Video sources failed (expected): {response.status_code}")

        except Exception as e:
            print(f"⚠️ Video endpoint test failed: {e}")

    def test_trailer_endpoint(self):
        """Test trailer extraction endpoint."""

        # Test with various trailer data
        test_cases = [
            {
                "name": "AniList trailer",
                "data": {"anilist_trailer": {"id": "dQw4w9WgXcQ", "site": "youtube"}},
            },
            {
                "name": "TMDB trailer",
                "data": {"tmdb_trailer": {"key": "dQw4w9WgXcQ", "site": "YouTube"}},
            },
        ]

        for case in test_cases:
            try:
                response = client.post("/sources/trailer", json=case["data"])

                if response.status_code == 200:
                    data = response.json()
                    self.capture_response("POST /sources/trailer", data)
                    print(f"✅ Trailer extraction ({case['name']}) successful")
                    break
                else:
                    error_data = (
                        response.json()
                        if response.headers.get("content-type") == "application/json"
                        else {"error": "Non-JSON response"}
                    )
                    self.capture_response(
                        "POST /sources/trailer", error_data, response.status_code
                    )
                    print(
                        f"⚠️ Trailer extraction ({case['name']}) failed: {response.status_code}"
                    )

            except Exception as e:
                print(f"⚠️ Trailer extraction ({case['name']}) error: {e}")

    def test_error_handling(self):
        """Test error responses for documentation."""

        # Test 404 - Invalid source
        response = client.get("/sources/invalid_source/popular")
        assert response.status_code == 404
        error_data = response.json()
        self.capture_response(
            "GET /sources/invalid_source/popular (404 Error)", error_data, 404
        )

        # Test 422 - Missing required parameter
        response = client.get(f"/sources/{self.test_source}/search")
        assert response.status_code == 422
        error_data = response.json()
        self.capture_response(
            "GET /sources/aniworld/search (422 Error)", error_data, 422
        )

        # Test 404 - Invalid season/episode
        response = client.get(
            f"/sources/{self.test_source}/series/seasons/999/episodes/999?url=test"
        )
        assert response.status_code == 404
        error_data = response.json()
        self.capture_response(
            "GET /sources/aniworld/series/seasons/999/episodes/999 (404 Error)",
            error_data,
            404,
        )

        print("✅ Error handling documented")

    def teardown_method(self):
        """Save individual test results."""
        if hasattr(self, "test_results") and self.test_results:
            # Append to existing results or create new file
            try:
                with open(
                    "tests/integration/comprehensive_test_results.json", "r"
                ) as f:
                    existing_results = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_results = {}

            existing_results.update(self.test_results)

            with open("tests/integration/comprehensive_test_results.json", "w") as f:
                json.dump(existing_results, f, indent=2, default=str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
