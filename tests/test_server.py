"""
Tests for YouTube Music MCP Server.

Uses unittest.mock to mock YTMusic so no real auth or network is needed.
Run with:  pytest tests/ -v
"""

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest

import server


# ─────────────────────────────────────────────
# Fixtures & helpers
# ─────────────────────────────────────────────

MOCK_SONGS = [
    {"title": "HUMBLE.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}, "videoId": "tvTRZJ-4EyI"},
    {"title": "DNA.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}, "videoId": "NLZRYQMLDW4"},
    {"title": "God's Plan", "artists": [{"name": "Drake"}], "album": {"name": "Scorpion"}, "videoId": "xpVfcZ0ZcFM"},
    {"title": "Sicko Mode", "artists": [{"name": "Travis Scott"}], "album": {"name": "Astroworld"}, "videoId": "6ONRf7h3Mdk"},
    {"title": "Rockstar", "artists": [{"name": "Post Malone"}], "album": {"name": "Beerbongs"}, "videoId": "UceaB4D0jpo"},
    {"title": "Sunflower", "artists": [{"name": "Post Malone"}], "album": {"name": "Spider-Man"}, "videoId": "ApXoWvfEYVU"},
]

MOCK_PLAYLISTS = [
    {"title": "Rap Favourites", "playlistId": "PLrandom1", "count": 42},
    {"title": "Late Night Chill", "playlistId": "PLrandom2", "count": 18},
]

MOCK_SEARCH_RESULTS = [
    {"resultType": "song", "title": "HUMBLE.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}, "videoId": "tvTRZJ-4EyI"},
    {"resultType": "song", "title": "DNA.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}, "videoId": "NLZRYQMLDW4"},
    {"resultType": "album", "title": "DAMN.", "artists": [{"name": "Kendrick Lamar"}]},
    {"resultType": "artist", "artist": "Kendrick Lamar"},
]

MOCK_WATCH_PLAYLIST = {
    "tracks": [
        {"title": "Money Trees", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "good kid"}, "videoId": "ydR3WN5yVU8"},
        {"title": "Poetic Justice", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "good kid"}, "videoId": "6Sl_3RB4OJo"},
        {"title": "Backseat Freestyle", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "good kid"}, "videoId": "Jg5wkZ-dJXA"},
    ]
}

MOCK_HISTORY = [
    {"title": "HUMBLE.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}},
    {"title": "DNA.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}},
    {"title": "God's Plan", "artists": [{"name": "Drake"}], "album": {"name": "Scorpion"}},
]

MOCK_MOOD_CATEGORIES = {
    "For you": [
        {"title": "Chill Vibes", "params": "params_chill"},
        {"title": "Workout Beats", "params": "params_workout"},
    ],
    "Genres": [
        {"title": "Hip-Hop", "params": "params_hiphop"},
        {"title": "Jazz", "params": "params_jazz"},
    ],
}

MOCK_MOOD_PLAYLISTS = [
    {"title": "Chill Mix", "playlistId": "PLchillmix"},
    {"title": "Relax Zone", "playlistId": "PLrelaxzone"},
]

MOCK_CHARTS = {
    "countries": {"selected": "ZZ", "options": ["US", "GB"]},
    "videos": [
        {"title": "Daily Top Music Videos - Global", "playlistId": "PLtop1"},
        {"title": "Daily Top Music Videos - US", "playlistId": "PLtop2"},
    ],
    "artists": [
        {"title": "Trending Artist 1", "browseId": "UC1", "subscribers": "10M", "rank": 1, "trend": "up"},
        {"title": "Trending Artist 2", "browseId": "UC2", "subscribers": "5M", "rank": 2, "trend": "neutral"},
    ],
}


def make_mock_yt() -> MagicMock:
    yt = MagicMock()
    yt.get_library_songs.return_value = MOCK_SONGS
    yt.get_library_playlists.return_value = MOCK_PLAYLISTS
    yt.search.return_value = MOCK_SEARCH_RESULTS
    yt.get_watch_playlist.return_value = MOCK_WATCH_PLAYLIST
    yt.get_history.return_value = MOCK_HISTORY
    yt.get_mood_categories.return_value = MOCK_MOOD_CATEGORIES
    yt.get_mood_playlists.return_value = MOCK_MOOD_PLAYLISTS
    yt.get_charts.return_value = MOCK_CHARTS
    yt.create_playlist.return_value = "PL_new_id"
    yt.add_playlist_items.return_value = {"status": "STATUS_SUCCEEDED"}
    yt.get_playlist.return_value = {"title": "Rap Favourites", "tracks": MOCK_SONGS[:3]}
    return yt


@pytest.fixture(autouse=True)
def reset_server_state():
    """Reset global server state before each test."""
    server._ytmusic = None
    server._auth_method = "none"
    server._cache.clear()
    yield
    server._ytmusic = None
    server._auth_method = "none"
    server._cache.clear()


@pytest.fixture
def mock_yt(tmp_path):
    """Patch get_yt() to return a mock YTMusic instance."""
    yt = make_mock_yt()
    with patch("server.get_yt", return_value=yt):
        yield yt


# ─────────────────────────────────────────────
# Auth & Initialization tests
# ─────────────────────────────────────────────

class TestAuth:
    def test_raises_auth_error_when_no_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(server, "_OAUTH_PATH", tmp_path / "oauth.json")
        monkeypatch.setattr(server, "_BROWSER_PATH", tmp_path / "browser.json")
        monkeypatch.setattr(server, "_COOKIE_PATH", tmp_path / "cookie.txt")
        with pytest.raises(server.AuthError, match="No auth file"):
            server.get_yt()

    def test_uses_oauth_when_present(self, tmp_path, monkeypatch):
        oauth_path = tmp_path / "oauth.json"
        oauth_path.write_text("{}")
        monkeypatch.setattr(server, "_OAUTH_PATH", oauth_path)
        monkeypatch.setattr(server, "_BROWSER_PATH", tmp_path / "browser.json")
        monkeypatch.setattr(server, "_COOKIE_PATH", tmp_path / "cookie.txt")
        with patch("server.YTMusic") as MockYT:
            MockYT.return_value = MagicMock()
            server.get_yt()
            MockYT.assert_called_once_with(str(oauth_path))
            assert server._auth_method == "oauth"

    def test_uses_browser_when_no_oauth(self, tmp_path, monkeypatch):
        browser_path = tmp_path / "browser.json"
        browser_path.write_text("{}")
        monkeypatch.setattr(server, "_OAUTH_PATH", tmp_path / "oauth.json")
        monkeypatch.setattr(server, "_BROWSER_PATH", browser_path)
        monkeypatch.setattr(server, "_COOKIE_PATH", tmp_path / "cookie.txt")
        with patch("server.YTMusic") as MockYT:
            MockYT.return_value = MagicMock()
            server.get_yt()
            MockYT.assert_called_once_with(str(browser_path))
            assert server._auth_method == "browser"

    def test_auto_generates_browser_json_from_cookie(self, tmp_path, monkeypatch):
        """cookie.txt should auto-generate browser.json when neither oauth nor browser exist."""
        cookie_path = tmp_path / "cookie.txt"
        browser_path = tmp_path / "browser.json"
        cookie_path.write_text("SAPISID=abc123; SID=xyz456; OTHER=val")
        monkeypatch.setattr(server, "_OAUTH_PATH", tmp_path / "oauth.json")
        monkeypatch.setattr(server, "_BROWSER_PATH", browser_path)
        monkeypatch.setattr(server, "_COOKIE_PATH", cookie_path)
        with patch("server.YTMusic") as MockYT:
            MockYT.return_value = MagicMock()
            server.get_yt()
            assert browser_path.exists()
            MockYT.assert_called_once_with(str(browser_path))
            assert "cookie" in server._auth_method.lower()
            # Verify the generated browser.json has the right keys
            import json
            data = json.loads(browser_path.read_text())
            assert data["Cookie"] == "SAPISID=abc123; SID=xyz456; OTHER=val"
            assert "authorization" in data  # SAPISIDHASH required by ytmusicapi
            assert data["authorization"].startswith("SAPISIDHASH ")

    def test_cookie_txt_rejects_invalid_cookies(self, tmp_path, monkeypatch):
        """cookie.txt without SAPISID/SID should raise AuthError."""
        cookie_path = tmp_path / "cookie.txt"
        cookie_path.write_text("RANDOM_COOKIE=somevalue; OTHER=thing")
        monkeypatch.setattr(server, "_OAUTH_PATH", tmp_path / "oauth.json")
        monkeypatch.setattr(server, "_BROWSER_PATH", tmp_path / "browser.json")
        monkeypatch.setattr(server, "_COOKIE_PATH", cookie_path)
        with pytest.raises(server.AuthError, match="does not look like a valid"):
            server.get_yt()

    def test_singleton_returns_same_instance(self, tmp_path, monkeypatch):
        oauth_path = tmp_path / "oauth.json"
        oauth_path.write_text("{}")
        monkeypatch.setattr(server, "_OAUTH_PATH", oauth_path)
        monkeypatch.setattr(server, "_BROWSER_PATH", tmp_path / "browser.json")
        monkeypatch.setattr(server, "_COOKIE_PATH", tmp_path / "cookie.txt")
        with patch("server.YTMusic") as MockYT:
            MockYT.return_value = MagicMock()
            yt1 = server.get_yt()
            yt2 = server.get_yt()
            assert yt1 is yt2
            assert MockYT.call_count == 1


# ─────────────────────────────────────────────
# Cache tests
# ─────────────────────────────────────────────

class TestCache:
    def test_cache_miss_returns_none(self):
        assert server._cache_get("missing") is None

    def test_cache_set_and_get(self):
        server._cache_set("key1", {"data": 42})
        assert server._cache_get("key1") == {"data": 42}

    def test_cache_expires_after_ttl(self):
        server._cache_set("expiring", "value")
        # Manually age the cache entry
        _, (val, ts) = "expiring", server._cache["expiring"]
        server._cache["expiring"] = (val, ts - server.CACHE_TTL - 1)
        assert server._cache_get("expiring") is None

    def test_cache_invalidate_by_prefix(self):
        server._cache_set("library_songs", [1, 2, 3])
        server._cache_set("library_playlists", [4, 5])
        server._cache_set("other_key", "keep_me")
        server._cache_invalidate("library_")
        assert server._cache_get("library_songs") is None
        assert server._cache_get("library_playlists") is None
        assert server._cache_get("other_key") == "keep_me"

    def test_library_songs_cached_on_second_call(self, mock_yt):
        server._get_library_songs_cached()
        server._get_library_songs_cached()
        # Should only call YTMusic once (second call is cached)
        mock_yt.get_library_songs.assert_called_once()


# ─────────────────────────────────────────────
# Helper tests
# ─────────────────────────────────────────────

class TestHelpers:
    def test_artist_name_from_string(self):
        assert server._artist_name("Adele") == "Adele"

    def test_artist_name_from_dict(self):
        assert server._artist_name({"name": "Beyoncé"}) == "Beyoncé"

    def test_artist_name_unknown_for_empty_dict(self):
        assert server._artist_name({}) == "Unknown Artist"

    def test_artist_name_unknown_for_other_types(self):
        assert server._artist_name(None) == "Unknown Artist"  # type: ignore

    def test_song_to_dict(self):
        song = {"title": "HUMBLE.", "artists": [{"name": "Kendrick Lamar"}], "album": {"name": "DAMN."}, "videoId": "abc"}
        result = server._song_to_dict(song)
        assert result["title"] == "HUMBLE."
        assert result["artist"] == "Kendrick Lamar"
        assert result["album"] == "DAMN."
        assert result["videoId"] == "abc"

    def test_artist_counts(self):
        counts = server._artist_counts(MOCK_SONGS)
        assert counts["Kendrick Lamar"] == 2
        assert counts["Post Malone"] == 2
        assert counts["Drake"] == 1


# ─────────────────────────────────────────────
# Tool tests
# ─────────────────────────────────────────────

class TestTools:
    def test_get_liked_songs_count(self, mock_yt):
        result = asyncio.run(server.tool_get_liked_songs_count())
        data = json.loads(result[0].text)
        assert data["total_songs"] == 6

    def test_get_library_stats_basic(self, mock_yt):
        result = asyncio.run(server.tool_get_library_stats(detailed=False))
        data = json.loads(result[0].text)
        assert data["total_songs"] == 6
        assert "unique_artists" in data
        assert "total_playlists" in data

    def test_get_library_stats_detailed(self, mock_yt):
        result = asyncio.run(server.tool_get_library_stats(detailed=True))
        data = json.loads(result[0].text)
        assert "top_artists" in data
        assert len(data["top_artists"]) > 0

    def test_get_top_artists_returns_ranked(self, mock_yt):
        result = asyncio.run(server.tool_get_top_artists(limit=3))
        data = json.loads(result[0].text)
        artists = [a["artist"] for a in data["artists"]]
        assert "Kendrick Lamar" in artists or "Post Malone" in artists
        assert data["artists"][0]["rank"] == 1

    def test_search_music_returns_formatted(self, mock_yt):
        result = asyncio.run(server.tool_search_music("Kendrick", "all", 10))
        data = json.loads(result[0].text)
        assert data["query"] == "Kendrick"
        titles = [r["title"] for r in data["results"]]
        assert "HUMBLE." in titles

    def test_search_music_no_results(self, mock_yt):
        mock_yt.search.return_value = []
        result = asyncio.run(server.tool_search_music("xyznonexistent", "all", 5))
        data = json.loads(result[0].text)
        assert len(data["results"]) == 0

    def test_find_similar_songs_uses_radio(self, mock_yt):
        result = asyncio.run(server.tool_find_similar_songs("HUMBLE. Kendrick", limit=3))
        data = json.loads(result[0].text)
        assert "seed" in data
        assert "similar_songs" in data
        mock_yt.get_watch_playlist.assert_called_once()
        call_kwargs = mock_yt.get_watch_playlist.call_args
        assert call_kwargs.kwargs.get("radio") is True or (len(call_kwargs.args) > 2 and True)

    def test_find_similar_songs_no_seed_raises(self, mock_yt):
        mock_yt.search.return_value = [{"resultType": "artist", "artist": "Nobody"}]
        with pytest.raises(server.SearchError):
            asyncio.run(server.tool_find_similar_songs("xyzfake", limit=5))

    def test_get_recommendations_parallel(self, mock_yt):
        result = asyncio.run(server.tool_get_recommendations(count=5))
        data = json.loads(result[0].text)
        assert "recommendations" in data
        assert "based_on_artists" in data

    def test_list_playlists(self, mock_yt):
        result = asyncio.run(server.tool_list_playlists(limit=10))
        data = json.loads(result[0].text)
        titles = [p["title"] for p in data["playlists"]]
        assert "Rap Favourites" in titles
        assert "Late Night Chill" in titles

    def test_get_playlist_songs(self, mock_yt):
        result = asyncio.run(server.tool_get_playlist_songs("PLrandom1", limit=10))
        data = json.loads(result[0].text)
        assert data["title"] == "Rap Favourites"
        assert data["playlistId"] == "PLrandom1"
        mock_yt.get_playlist.assert_called_once_with("PLrandom1", limit=10)

    def test_create_playlist_success(self, mock_yt):
        result = asyncio.run(server.tool_create_playlist_from_songs(
            "My Test Playlist", ["HUMBLE. Kendrick", "God's Plan Drake"], "test desc", "PRIVATE"
        ))
        data = json.loads(result[0].text)
        assert data["playlistId"] == "PL_new_id"
        assert data["success"] is True

    def test_add_songs_to_playlist(self, mock_yt):
        result = asyncio.run(server.tool_add_songs_to_playlist("PLrandom1", ["HUMBLE. Kendrick"]))
        data = json.loads(result[0].text)
        assert data["success"] is True
        assert len(data["added_songs"]) > 0
        mock_yt.add_playlist_items.assert_called_once()

    def test_explore_moods(self, mock_yt):
        result = asyncio.run(server.tool_explore_moods())
        data = json.loads(result[0].text)
        all_cats = [c for s in data["mood_categories"] for c in s["categories"]]
        assert "Chill Vibes" in all_cats
        assert "Workout Beats" in all_cats

    def test_get_charts_global(self, mock_yt):
        result = asyncio.run(server.tool_get_charts("ZZ"))
        data = json.loads(result[0].text)
        assert data["country"] == "ZZ"
        assert data["trending_playlists"][0]["title"] == "Daily Top Music Videos - Global"
        assert data["trending_artists"][0]["name"] == "Trending Artist 1"
        mock_yt.get_charts.assert_called_once_with(country="ZZ")

    def test_get_listening_insights(self, mock_yt):
        result = asyncio.run(server.tool_get_listening_insights())
        data = json.loads(result[0].text)
        assert data["total_tracks"] == 3
        assert data["top_artists"][0]["artist"] == "Kendrick Lamar"
        assert "insight" in data

    def test_get_server_info(self, mock_yt):
        result = asyncio.run(server.tool_get_server_info())
        data = json.loads(result[0].text)
        assert data["version"] == "2.0.0"
        assert data["capabilities"]["tools"] == 15
        assert data["capabilities"]["resources"] == 3
        assert data["capabilities"]["prompts"] == 3

    def test_build_smart_playlist_matched(self, mock_yt):
        mock_yt.get_playlist.return_value = {
            "title": "Chill Mix",
            "tracks": [
                {"title": "Chill Song", "artists": [{"name": "Artist X"}], "videoId": "abc123", "duration_seconds": 300},
            ]
        }
        result = asyncio.run(server.tool_build_smart_playlist("chill", "", "medium", 5))
        data = json.loads(result[0].text)
        assert data["mood"] == "chill"
        assert "steps" in data
        assert "tracks" in data


# ─────────────────────────────────────────────
# Resource tests
# ─────────────────────────────────────────────

class TestResources:
    def test_list_resources_count(self):
        assert len(server.RESOURCES) == 3

    def test_resource_uris(self):
        uris = [str(r.uri) for r in server.RESOURCES]
        assert "library://songs" in uris
        assert "library://artists" in uris
        assert "library://playlists" in uris

    def test_read_songs_resource(self, mock_yt):
        result = asyncio.run(server.read_resource("library://songs"))
        data = json.loads(result.contents[0].text)
        assert len(data) == 6
        assert data[0]["title"] == "HUMBLE."
        assert data[0]["artist"] == "Kendrick Lamar"

    def test_read_artists_resource(self, mock_yt):
        result = asyncio.run(server.read_resource("library://artists"))
        data = json.loads(result.contents[0].text)
        assert data[0]["rank"] == 1
        assert "artist" in data[0]
        assert "songs" in data[0]
        assert "percentage" in data[0]

    def test_read_playlists_resource(self, mock_yt):
        result = asyncio.run(server.read_resource("library://playlists"))
        data = json.loads(result.contents[0].text)
        assert len(data) == 2
        assert data[0]["title"] == "Rap Favourites"

    def test_read_unknown_resource_raises(self, mock_yt):
        with pytest.raises(ValueError, match="Unknown resource URI"):
            asyncio.run(server.read_resource("library://unknown"))


# ─────────────────────────────────────────────
# Prompt tests
# ─────────────────────────────────────────────

class TestPrompts:
    def test_list_prompts_count(self):
        assert len(server.PROMPTS) == 3

    def test_prompt_names(self):
        names = [p.name for p in server.PROMPTS]
        assert "weekly-discovery-mix" in names
        assert "mood-based-playlist" in names
        assert "artist-deep-dive" in names

    def test_weekly_discovery_prompt(self):
        result = asyncio.run(server.get_prompt("weekly-discovery-mix", {"discovery_style": "adventurous"}))
        text = result.messages[0].content.text
        assert "weekly" in text.lower() or "discovery" in text.lower()
        assert "get_library_stats" in text

    def test_mood_playlist_prompt(self):
        result = asyncio.run(server.get_prompt("mood-based-playlist", {"mood": "focus", "duration_minutes": "45"}))
        text = result.messages[0].content.text
        assert "focus" in text
        assert "45" in text
        assert "build_smart_playlist" in text

    def test_artist_deep_dive_prompt(self):
        result = asyncio.run(server.get_prompt("artist-deep-dive", {"artist_name": "The Weeknd"}))
        text = result.messages[0].content.text
        assert "The Weeknd" in text
        assert "find_similar_songs" in text

    def test_artist_deep_dive_missing_artist_raises(self):
        with pytest.raises(ValueError, match="artist_name is required"):
            asyncio.run(server.get_prompt("artist-deep-dive", {}))

    def test_unknown_prompt_raises(self):
        with pytest.raises(ValueError, match="Unknown prompt"):
            asyncio.run(server.get_prompt("nonexistent-prompt", {}))


# ─────────────────────────────────────────────
# Tool routing (call_tool dispatcher)
# ─────────────────────────────────────────────

class TestToolRouting:
    def test_unknown_tool_returns_error(self, mock_yt):
        result = asyncio.run(server.call_tool("totally_fake_tool", {}))
        data = json.loads(result[0].text)
        assert "error" in data

    def test_missing_required_arg_returns_error(self, mock_yt):
        result = asyncio.run(server.call_tool("search_music", {}))
        data = json.loads(result[0].text)
        assert "error" in data

    def test_call_get_liked_songs_count(self, mock_yt):
        result = asyncio.run(server.call_tool("get_liked_songs_count", {}))
        data = json.loads(result[0].text)
        assert data["total_songs"] == 6

    def test_call_search_music(self, mock_yt):
        result = asyncio.run(server.call_tool("search_music", {"query": "Kendrick", "filter_type": "songs"}))
        data = json.loads(result[0].text)
        titles = [r["title"] for r in data["results"]]
        assert "HUMBLE." in titles

    def test_call_get_server_info(self, mock_yt):
        result = asyncio.run(server.call_tool("get_server_info", {}))
        data = json.loads(result[0].text)
        assert data["version"] == "2.0.0"
