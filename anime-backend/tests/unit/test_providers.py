"""Unit tests for anime providers."""

import pytest

from lib.models.base import SourcePreference
from lib.providers.aniworld import AniWorldProvider
from lib.providers.serienstream import SerienStreamProvider


class TestAniWorldProvider:
    """Test cases for AniWorldProvider."""

    def test_initialization(self, aniworld_provider):
        """Test AniWorld provider initialization."""
        assert aniworld_provider.source.name == "AniWorld"
        assert aniworld_provider.source.lang == "de"
        assert aniworld_provider.source.base_url == "https://aniworld.to"
        assert aniworld_provider.source.version == "0.3.8"

    def test_get_source_preferences(self, aniworld_provider):
        """Test AniWorld source preferences."""
        preferences = aniworld_provider.get_source_preferences()

        assert isinstance(preferences, list)
        assert len(preferences) == 6

        # Check preference keys
        keys = [p.key for p in preferences]
        expected_keys = ["lang", "type", "res", "host", "lang_filter", "host_filter"]
        assert keys == expected_keys

        # Test language preference
        lang_pref = preferences[0]
        assert lang_pref.key == "lang"
        assert lang_pref.list_preference is not None
        assert lang_pref.list_preference["title"] == "Bevorzugte Sprache"
        assert lang_pref.list_preference["entries"] == ["Deutsch", "Englisch"]
        assert lang_pref.list_preference["entryValues"] == ["Deutscher", "Englischer"]

        # Test type preference
        type_pref = preferences[1]
        assert type_pref.key == "type"
        assert type_pref.list_preference["entries"] == ["Dub", "Sub"]

        # Test resolution preference
        res_pref = preferences[2]
        assert res_pref.key == "res"
        assert "1080p" in res_pref.list_preference["entries"]
        assert "720p" in res_pref.list_preference["entries"]
        assert "480p" in res_pref.list_preference["entries"]

        # Test host preference
        host_pref = preferences[3]
        assert host_pref.key == "host"
        expected_hosts = [
            "Doodstream",
            "Filemoon",
            "Luluvdo",
            "SpeedFiles",
            "Streamtape",
            "Vidmoly",
            "Vidoza",
            "VOE",
        ]
        assert host_pref.list_preference["entries"] == expected_hosts

        # Test multi-select preferences
        lang_filter_pref = preferences[4]
        assert lang_filter_pref.key == "lang_filter"
        assert lang_filter_pref.multi_select_list_preference is not None
        assert (
            "Deutscher Dub" in lang_filter_pref.multi_select_list_preference["entries"]
        )

        host_filter_pref = preferences[5]
        assert host_filter_pref.key == "host_filter"
        assert host_filter_pref.multi_select_list_preference is not None


class TestSerienStreamProvider:
    """Test cases for SerienStreamProvider."""

    def test_initialization(self, serienstream_provider):
        """Test SerienStream provider initialization."""
        assert serienstream_provider.source.name == "SerienStream"
        assert serienstream_provider.source.lang == "de"
        assert serienstream_provider.source.base_url == "https://s.to"
        assert serienstream_provider.source.version == "0.0.9"

    def test_get_source_preferences(self, serienstream_provider):
        """Test SerienStream source preferences."""
        preferences = serienstream_provider.get_source_preferences()

        assert isinstance(preferences, list)
        assert len(preferences) == 6

        # Should have same structure as AniWorld
        keys = [p.key for p in preferences]
        expected_keys = ["lang", "type", "res", "host", "lang_filter", "host_filter"]
        assert keys == expected_keys

        # Test that preferences are properly structured
        for pref in preferences:
            assert isinstance(pref, SourcePreference)
            assert pref.key in expected_keys

            # Check that each preference has either list_preference or multi_select_list_preference
            if pref.key in ["lang", "type", "res", "host"]:
                assert pref.list_preference is not None
                assert pref.multi_select_list_preference is None
            else:
                assert pref.list_preference is None
                assert pref.multi_select_list_preference is not None


class TestProviderHelpers:
    """Test helper methods in providers."""

    def test_clean_html_string(self, aniworld_provider):
        """Test HTML string cleaning."""
        dirty_html = "&lt;div&gt;Test &amp; More&lt;/div&gt;"
        cleaned = aniworld_provider.clean_html_string(dirty_html)
        # Note: &amp; is not handled by our clean_html_string function
        assert cleaned == "<div>Test &amp; More</div>"

        # Test with None input
        assert aniworld_provider.clean_html_string(None) == ""

        # Test with empty string
        assert aniworld_provider.clean_html_string("") == ""

    def test_clean_html_string_complex(self, serienstream_provider):
        """Test HTML string cleaning with complex content."""
        complex_html = "Line 1<br>Line 2&lt;br&gt;Line 3&#039;s test&quot;quoted&quot;"
        expected = 'Line 1\nLine 2\nLine 3\'s test"quoted"'
        cleaned = serienstream_provider.clean_html_string(complex_html)
        assert cleaned == expected
