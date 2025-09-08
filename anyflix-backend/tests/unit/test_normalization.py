"""Tests for series normalization utilities."""

import pytest

from lib.models.base import Episode, Movie, MovieKind, Season, SeriesDetail
from lib.utils.normalization import (
    _parse_episode_name,
    _parse_movie_name,
    normalize_series_detail,
    series_detail_to_legacy_episodes,
)


class TestEpisodeParsing:
    """Test episode name parsing functionality."""

    def test_parse_episode_normal_format(self):
        """Test parsing normal episode format."""
        episode = _parse_episode_name(
            "Staffel 4 Folge 30 : The Final Chapter Part 2",
            "/anime/stream/attack-on-titan/staffel-4/episode-30",
            None,
        )

        assert episode is not None
        assert episode.season == 4
        assert episode.episode == 30
        assert episode.title == "The Final Chapter Part 2"
        assert episode.url == "/anime/stream/attack-on-titan/staffel-4/episode-30"
        assert episode.tags == []

    def test_parse_episode_with_tags(self):
        """Test parsing episode with tags in brackets."""
        episode = _parse_episode_name(
            "Staffel 4 Folge 30 : The Final Chapter Part 2 [Series Final Episode]",
            "/anime/stream/attack-on-titan/staffel-4/episode-30",
            None,
        )

        assert episode is not None
        assert episode.season == 4
        assert episode.episode == 30
        assert episode.title == "The Final Chapter Part 2"
        assert episode.tags == ["Series Final Episode"]

    def test_parse_episode_multiple_tags(self):
        """Test parsing episode with multiple tags."""
        episode = _parse_episode_name(
            "Staffel 1 Folge 1 : First Episode [HD] [Sub]",
            "/anime/stream/attack-on-titan/staffel-1/episode-1",
            None,
        )

        assert episode is not None
        assert episode.season == 1
        assert episode.episode == 1
        assert episode.title == "First Episode"
        assert episode.tags == ["HD", "Sub"]

    def test_parse_episode_url_fallback(self):
        """Test parsing when name format fails but URL works."""
        episode = _parse_episode_name(
            "Some weird format: Episode Title",
            "/anime/stream/attack-on-titan/staffel-2/episode-15",
            None,
        )

        assert episode is not None
        assert episode.season == 2
        assert episode.episode == 15
        assert episode.title == "Episode Title"

    def test_parse_episode_invalid(self):
        """Test parsing invalid episode format."""
        episode = _parse_episode_name(
            "Film 1 : This is a movie",
            "/anime/stream/attack-on-titan/filme/film-1",
            None,
        )

        assert episode is None

    def test_parse_episode_spaces_variation(self):
        """Test parsing with different spacing."""
        episode = _parse_episode_name(
            "Staffel  2  Folge  5  :  Space Variation",
            "/anime/stream/test/staffel-2/episode-5",
            None,
        )

        assert episode is not None
        assert episode.season == 2
        assert episode.episode == 5
        assert episode.title == "Space Variation"


class TestMovieParsing:
    """Test movie name parsing functionality."""

    def test_parse_movie_normal_format(self):
        """Test parsing normal movie format."""
        movie = _parse_movie_name(
            "Film 6 : Lost in the Cruel World",
            "/anime/stream/attack-on-titan/filme/film-6",
            None,
        )

        assert movie is not None
        assert movie.number == 6
        assert movie.title == "Lost in the Cruel World"
        assert movie.kind == MovieKind.MOVIE
        assert movie.url == "/anime/stream/attack-on-titan/filme/film-6"
        assert movie.tags == []

    def test_parse_movie_with_ova_tag(self):
        """Test parsing movie with OVA tag."""
        movie = _parse_movie_name(
            "Film 11 : Great need [OVA]",
            "/anime/stream/attack-on-titan/filme/film-11",
            None,
        )

        assert movie is not None
        assert movie.number == 11
        assert movie.title == "Great need"
        assert movie.kind == MovieKind.OVA

    def test_parse_movie_with_movie_tag(self):
        """Test parsing movie with Movie tag."""
        movie = _parse_movie_name(
            "Film 12 : The Last Attack [Movie]",
            "/anime/stream/attack-on-titan/filme/film-12",
            None,
        )

        assert movie is not None
        assert movie.number == 12
        assert movie.title == "The Last Attack"
        assert movie.kind == MovieKind.MOVIE

    def test_parse_movie_no_space_before_bracket(self):
        """Test parsing movie without space before bracket."""
        movie = _parse_movie_name(
            "Film 5 : Some Title[OVA]", "/anime/stream/test/filme/film-5", None
        )

        assert movie is not None
        assert movie.number == 5
        assert movie.title == "Some Title"
        assert movie.kind == MovieKind.OVA

    def test_parse_movie_url_fallback(self):
        """Test parsing when name format fails but URL works."""
        movie = _parse_movie_name(
            "Weird format: Movie Title", "/anime/stream/test/filme/film-3", None
        )

        assert movie is not None
        assert movie.number == 3
        assert movie.title == "Movie Title"
        assert movie.kind == MovieKind.MOVIE

    def test_parse_movie_invalid(self):
        """Test parsing invalid movie format."""
        movie = _parse_movie_name(
            "Staffel 1 Folge 1 : This is an episode",
            "/anime/stream/test/staffel-1/episode-1",
            None,
        )

        assert movie is None

    def test_parse_movie_additional_tags(self):
        """Test parsing movie with additional tags."""
        movie = _parse_movie_name(
            "Film 7 : Special Movie [Movie] [HD]",
            "/anime/stream/test/filme/film-7",
            None,
        )

        assert movie is not None
        assert movie.number == 7
        assert movie.title == "Special Movie"
        assert movie.kind == MovieKind.MOVIE
        assert movie.tags == ["HD"]


class TestNormalization:
    """Test series normalization functionality."""

    def test_normalize_attack_on_titan_sample(self):
        """Test normalization with Attack on Titan sample data."""
        sample_data = {
            "episodes": [
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
            ]
        }

        result = normalize_series_detail(sample_data, "attack-on-titan")

        assert result.slug == "attack-on-titan"
        assert len(result.seasons) == 3
        assert len(result.movies) == 2

        # Check seasons are sorted
        assert result.seasons[0].season == 1
        assert result.seasons[1].season == 3
        assert result.seasons[2].season == 4

        # Check season 4 has 2 episodes
        season_4 = result.seasons[2]
        assert len(season_4.episodes) == 2
        assert season_4.episodes[0].episode == 29
        assert season_4.episodes[1].episode == 30
        assert season_4.episodes[1].tags == ["Series Final Episode"]

        # Check movies are sorted
        assert result.movies[0].number == 11
        assert result.movies[0].kind == MovieKind.OVA
        assert result.movies[1].number == 12
        assert result.movies[1].kind == MovieKind.MOVIE

    def test_normalize_empty_data(self):
        """Test normalization with empty data."""
        result = normalize_series_detail({"episodes": []}, "test")

        assert result.slug == "test"
        assert result.seasons == []
        assert result.movies == []

    def test_normalize_mixed_valid_invalid(self):
        """Test normalization with mix of valid and invalid entries."""
        data = {
            "episodes": [
                {
                    "name": "Staffel 1 Folge 1 : Valid Episode",
                    "url": "/anime/stream/test/staffel-1/episode-1",
                    "date_upload": None,
                },
                {
                    "name": "Invalid Format",
                    "url": "/some/invalid/url",
                    "date_upload": None,
                },
                {
                    "name": "Film 1 : Valid Movie",
                    "url": "/anime/stream/test/filme/film-1",
                    "date_upload": None,
                },
                {
                    "name": "",  # Empty name
                    "url": "/anime/stream/test/staffel-2/episode-1",
                    "date_upload": None,
                },
            ]
        }

        result = normalize_series_detail(data, "test")

        assert len(result.seasons) == 1
        assert len(result.seasons[0].episodes) == 1
        assert len(result.movies) == 1

    def test_normalize_auto_slug_extraction(self):
        """Test automatic slug extraction from URLs."""
        data = {
            "episodes": [
                {
                    "name": "Staffel 1 Folge 1 : Test Episode",
                    "url": "/anime/stream/my-anime-series/staffel-1/episode-1",
                    "date_upload": None,
                }
            ]
        }

        result = normalize_series_detail(data)  # No slug provided

        assert result.slug == "my-anime-series"


class TestLegacyConversion:
    """Test conversion back to legacy format."""

    def test_series_detail_to_legacy_episodes(self):
        """Test conversion from SeriesDetail to legacy episodes."""
        series = SeriesDetail(
            slug="test",
            seasons=[
                Season(
                    season=1,
                    title="Staffel 1",
                    episodes=[
                        Episode(
                            season=1,
                            episode=1,
                            title="First Episode",
                            url="/anime/stream/test/staffel-1/episode-1",
                            tags=["HD"],
                        ),
                        Episode(
                            season=1,
                            episode=2,
                            title="Second Episode",
                            url="/anime/stream/test/staffel-1/episode-2",
                            tags=[],
                        ),
                    ],
                )
            ],
            movies=[
                Movie(
                    number=1,
                    title="Test Movie",
                    kind=MovieKind.MOVIE,
                    url="/anime/stream/test/filme/film-1",
                    tags=[],
                ),
                Movie(
                    number=2,
                    title="Test OVA",
                    kind=MovieKind.OVA,
                    url="/anime/stream/test/filme/film-2",
                    tags=["Special"],
                ),
            ],
        )

        legacy_episodes = series_detail_to_legacy_episodes(series)

        assert len(legacy_episodes) == 4
        assert legacy_episodes[0].name == "Staffel 1 Folge 1 : First Episode [HD]"
        assert legacy_episodes[1].name == "Staffel 1 Folge 2 : Second Episode"
        assert legacy_episodes[2].name == "Film 1 : Test Movie [Movie]"
        assert legacy_episodes[3].name == "Film 2 : Test OVA [OVA] [Special]"

    def test_roundtrip_conversion(self):
        """Test roundtrip conversion: flat -> hierarchical -> flat."""
        original_data = {
            "episodes": [
                {
                    "name": "Staffel 1 Folge 1 : Test Episode [HD]",
                    "url": "/anime/stream/test/staffel-1/episode-1",
                    "date_upload": None,
                },
                {
                    "name": "Film 1 : Test Movie [OVA]",
                    "url": "/anime/stream/test/filme/film-1",
                    "date_upload": None,
                },
            ]
        }

        # Convert to hierarchical
        series_detail = normalize_series_detail(original_data, "test")

        # Convert back to flat
        legacy_episodes = series_detail_to_legacy_episodes(series_detail)

        # Should match original (order might be different due to sorting)
        episode_names = {ep.name for ep in legacy_episodes}
        original_names = {ep["name"] for ep in original_data["episodes"]}

        assert episode_names == original_names


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_malformed_episode_names(self):
        """Test handling of malformed episode names."""
        data = {
            "episodes": [
                {
                    "name": "Staffel Folge : Missing Numbers",
                    "url": "/anime/stream/test/staffel-1/episode-1",
                    "date_upload": None,
                },
                {
                    "name": "Staffel 1 Folge : Missing Episode Number",
                    "url": "/anime/stream/test/staffel-1/episode-2",
                    "date_upload": None,
                },
                {
                    "name": " Folge 3 : Missing Season",
                    "url": "/anime/stream/test/staffel-1/episode-3",
                    "date_upload": None,
                },
            ]
        }

        result = normalize_series_detail(data, "test")

        # URL fallback should work for all three (the third one also extracts from URL)
        assert len(result.seasons) == 1
        assert len(result.seasons[0].episodes) == 3

    def test_special_characters_in_titles(self):
        """Test handling of special characters in titles."""
        data = {
            "episodes": [
                {
                    "name": 'Staffel 1 Folge 1 : Title with "Quotes" & Special [HD]',
                    "url": "/anime/stream/test/staffel-1/episode-1",
                    "date_upload": None,
                }
            ]
        }

        result = normalize_series_detail(data, "test")

        assert len(result.seasons) == 1
        episode = result.seasons[0].episodes[0]
        assert episode.title == 'Title with "Quotes" & Special'
        assert episode.tags == ["HD"]

    def test_very_high_numbers(self):
        """Test handling of very high season/episode numbers."""
        data = {
            "episodes": [
                {
                    "name": "Staffel 999 Folge 9999 : High Numbers",
                    "url": "/anime/stream/test/staffel-999/episode-9999",
                    "date_upload": None,
                }
            ]
        }

        result = normalize_series_detail(data, "test")

        assert len(result.seasons) == 1
        assert result.seasons[0].season == 999
        assert result.seasons[0].episodes[0].episode == 9999
