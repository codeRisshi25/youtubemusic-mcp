#!/usr/bin/env python3
"""
YouTube Music MCP Server

A Model Context Protocol (MCP) server bridging YouTube Music to AI assistants.
Implements tools, resources, and prompts for music discovery, library management,
playlist creation, mood-based exploration, and personalized recommendations.

Tools  (15): search, library stats, top artists, similar songs (real radio),
             recommendations (async), create/list/get/add playlists,
             smart playlist builder, mood explorer, charts, history insights,
             server info
Resources (3): library://songs  library://artists  library://playlists
Prompts   (3): weekly-discovery-mix  mood-based-playlist  artist-deep-dive
"""

import asyncio
import json
import logging
import time
from collections import Counter
from pathlib import Path
from typing import Any

import ytmusicapi
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    ReadResourceResult,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)
from ytmusicapi import YTMusic

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ytmusic-mcp")


# ─────────────────────────────────────────────
# Custom Exceptions
# ─────────────────────────────────────────────
class AuthError(RuntimeError):
    """Authentication file missing or invalid."""


class SearchError(RuntimeError):
    """Search returned no usable results."""


class PlaylistError(RuntimeError):
    """Playlist create/update operation failed."""


# ─────────────────────────────────────────────
# TTL Cache  (lightweight, no external deps)
# ─────────────────────────────────────────────
_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL = 300  # seconds (5 min)


def _cache_get(key: str) -> Any | None:
    if key in _cache:
        value, ts = _cache[key]
        if time.monotonic() - ts < CACHE_TTL:
            return value
        del _cache[key]
    return None


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = (value, time.monotonic())


def _cache_invalidate(prefix: str = "") -> None:
    for k in list(_cache):
        if k.startswith(prefix):
            del _cache[k]


# ─────────────────────────────────────────────
# YTMusic Singleton
# ─────────────────────────────────────────────
_ytmusic: YTMusic | None = None
_auth_method: str = "none"


def get_yt() -> YTMusic:
    global _ytmusic, _auth_method
    if _ytmusic is not None:
        return _ytmusic

    oauth_path = Path("oauth.json")
    browser_path = Path("browser.json")

    try:
        if oauth_path.exists():
            _ytmusic = YTMusic(str(oauth_path))
            _auth_method = "oauth"
            log.info("Authenticated via OAuth")
        elif browser_path.exists():
            _ytmusic = YTMusic(str(browser_path))
            _auth_method = "browser"
            log.info("Authenticated via browser cookies")
        else:
            raise AuthError(
                "No auth file found. Create oauth.json or browser.json — see README.md."
            )
        return _ytmusic
    except AuthError:
        raise
    except Exception as exc:
        raise AuthError(f"Failed to initialize YTMusic: {exc}") from exc


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _artist_name(artist: str | dict) -> str:
    if isinstance(artist, str):
        return artist
    if isinstance(artist, dict):
        return artist.get("name", "Unknown Artist")
    return "Unknown Artist"


def _fmt_song(song: dict, idx: int | None = None) -> str:
    title = song.get("title", "Unknown")
    artists = song.get("artists") or []
    artist = _artist_name(artists[0]) if artists else "Unknown Artist"
    album_obj = song.get("album") or {}
    album = album_obj.get("name", "") if isinstance(album_obj, dict) else ""
    prefix = f"{idx}. " if idx is not None else "• "
    line = f"{prefix}**{title}** — {artist}"
    if album:
        line += f"\n   _Album: {album}_"
    return line


def _get_library_songs_cached() -> list[dict]:
    cached = _cache_get("library_songs")
    if cached is not None:
        log.debug("Cache hit: library_songs")
        return cached
    yt = get_yt()
    log.info("Fetching full library (uncached)…")
    songs = yt.get_library_songs(limit=None)
    _cache_set("library_songs", songs)
    return songs


def _get_library_playlists_cached() -> list[dict]:
    cached = _cache_get("library_playlists")
    if cached is not None:
        return cached
    yt = get_yt()
    playlists = yt.get_library_playlists(limit=None)
    _cache_set("library_playlists", playlists)
    return playlists


def _artist_counts(songs: list[dict]) -> Counter:
    counts: Counter = Counter()
    for song in songs:
        artists = song.get("artists") or []
        if artists:
            counts[_artist_name(artists[0])] += 1
    return counts


# ─────────────────────────────────────────────
# Tool Handlers
# ─────────────────────────────────────────────

async def tool_get_liked_songs_count() -> list[TextContent]:
    songs = _get_library_songs_cached()
    return [TextContent(type="text", text=f"🎵 You have **{len(songs):,}** songs in your YouTube Music library.")]


async def tool_get_library_stats(detailed: bool = False) -> list[TextContent]:
    songs = _get_library_songs_cached()
    total = len(songs)
    counts = _artist_counts(songs)
    unique_artists = len(counts)

    lines = [
        "## 📊 Library Statistics\n",
        f"🎵 **Total Songs:** {total:,}",
        f"🎤 **Unique Artists:** {unique_artists:,}",
    ]

    if detailed and total > 0:
        avg = total / unique_artists if unique_artists else 0
        top5 = counts.most_common(5)
        lines.append(f"📈 **Avg Songs / Artist:** {avg:.1f}")
        lines.append("\n**Top 5 Artists:**")
        for artist, cnt in top5:
            pct = cnt / total * 100
            lines.append(f"  • {artist}: {cnt:,} songs ({pct:.1f}%)")

    playlists = _get_library_playlists_cached()
    lines.append(f"📝 **Playlists:** {len(playlists):,}")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_search_music(query: str, filter_type: str = "all", limit: int = 10) -> list[TextContent]:
    yt = get_yt()
    filter_map = {
        "songs": "songs", "albums": "albums", "artists": "artists",
        "playlists": "playlists", "videos": "videos", "all": None,
    }
    search_filter = filter_map.get(filter_type)
    results = yt.search(query, filter=search_filter, limit=limit)

    if not results:
        return [TextContent(type="text", text=f"🔍 No results for **\"{query}\"**.")]

    by_type: dict[str, list[dict]] = {}
    for item in results:
        rt = item.get("resultType", "other")
        by_type.setdefault(rt, []).append(item)

    icons = {"song": "🎵", "album": "💿", "artist": "🎤", "playlist": "📝", "video": "🎬"}
    out = [f"## 🔍 Search Results for \"{query}\"\n"]

    for rt, items in by_type.items():
        icon = icons.get(rt, "•")
        out.append(f"**{icon} {rt.capitalize()}s:**")
        for i, item in enumerate(items, 1):
            title = item.get("title") or item.get("artist", "Unknown")
            artists = item.get("artists") or []
            artist = _artist_name(artists[0]) if artists else ""
            album_obj = item.get("album") or {}
            album = album_obj.get("name", "") if isinstance(album_obj, dict) else ""
            line = f"{i}. **{title}**"
            if artist:
                line += f" — {artist}"
            if album:
                line += f" _(_{album}_)_"
            out.append(line)
        out.append("")

    return [TextContent(type="text", text="\n".join(out))]


async def tool_get_top_artists(limit: int = 10) -> list[TextContent]:
    songs = _get_library_songs_cached()
    if not songs:
        return [TextContent(type="text", text="📊 Library is empty.")]

    counts = _artist_counts(songs)
    total = len(songs)
    top = counts.most_common(limit)

    lines = [f"## 🎤 Top {min(limit, len(top))} Artists\n"]
    for i, (artist, cnt) in enumerate(top, 1):
        bar_len = int(cnt / top[0][1] * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        pct = cnt / total * 100
        lines.append(f"**{i}. {artist}**")
        lines.append(f"   `{bar}` {cnt:,} songs ({pct:.1f}%)\n")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_find_similar_songs(query: str, limit: int = 10) -> list[TextContent]:
    """Uses YTMusic's real watch playlist / radio — genuine similarity engine."""
    yt = get_yt()

    # 1. Find the seed song
    results = yt.search(query, filter="songs", limit=5)
    seed = next((r for r in results if r.get("resultType") == "song"), None)
    if not seed:
        raise SearchError(f'No song found matching "{query}".')

    seed_title = seed.get("title", "Unknown")
    seed_artists = seed.get("artists") or []
    seed_artist = _artist_name(seed_artists[0]) if seed_artists else "Unknown"
    video_id = seed.get("videoId")

    if not video_id:
        raise SearchError(f'Found "{seed_title}" but it has no video ID.')

    # 2. Get real YouTube Music radio/watch playlist for this song
    watch = yt.get_watch_playlist(videoId=video_id, radio=True, limit=limit + 1)
    tracks = watch.get("tracks", [])
    # Remove the seed song itself
    similar = [t for t in tracks if t.get("videoId") != video_id][:limit]

    lines = [
        f"## 🎧 Songs Similar to \"{seed_title}\" — {seed_artist}",
        "_Powered by YouTube Music Radio Engine_\n",
    ]

    if not similar:
        lines.append("No similar songs found via radio. Try a different song title.")
    else:
        for i, track in enumerate(similar, 1):
            title = track.get("title", "Unknown")
            artists = track.get("artists") or []
            artist = _artist_name(artists[0]) if artists else "Unknown Artist"
            album_obj = track.get("album") or {}
            album = album_obj.get("name", "") if isinstance(album_obj, dict) else ""
            line = f"{i}. **{title}** — {artist}"
            if album:
                line += f"\n   _Album: {album}_"
            lines.append(line)

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_get_recommendations(count: int = 20) -> list[TextContent]:
    """Async-parallel recommendations from top 5 artists + mood categories."""
    songs = _get_library_songs_cached()
    if not songs:
        return [TextContent(type="text", text="📊 Library empty — add songs first.")]

    counts = _artist_counts(songs)
    top_artists = [a for a, _ in counts.most_common(5)]
    yt = get_yt()

    async def fetch_artist(artist: str) -> list[dict]:
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, lambda: yt.search(artist, filter="songs", limit=12))
            return [r for r in results if r.get("resultType") == "song"]
        except Exception as exc:
            log.warning("Recommendation fetch failed for %s: %s", artist, exc)
            return []

    # Fetch all artists in parallel
    artist_results = await asyncio.gather(*[fetch_artist(a) for a in top_artists])

    seen: set[str] = set()
    recommendations: list[dict] = []
    for songs_list in artist_results:
        for song in songs_list:
            vid = song.get("videoId")
            if vid and vid not in seen:
                seen.add(vid)
                recommendations.append(song)
                if len(recommendations) >= count:
                    break
        if len(recommendations) >= count:
            break

    lines = [
        "## ✨ Personalized Recommendations",
        f"_Based on your top artists: {', '.join(top_artists[:3])}_\n",
    ]
    for i, song in enumerate(recommendations, 1):
        lines.append(_fmt_song(song, i))

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_create_playlist_from_songs(
    title: str,
    song_queries: list[str],
    description: str = "",
    privacy_status: str = "PRIVATE",
) -> list[TextContent]:
    yt = get_yt()
    lines = [f"## 📝 Creating Playlist: \"{title}\"\n"]
    if description:
        lines.append(f"_{description}_\n")

    found, not_found = [], []
    for query in song_queries:
        try:
            results = yt.search(query, filter="songs", limit=1)
            song = next((r for r in results if r.get("resultType") == "song"), None)
            if song and song.get("videoId"):
                found.append({"query": query, "song": song})
            else:
                not_found.append(query)
        except Exception as exc:
            log.warning("Search failed for '%s': %s", query, exc)
            not_found.append(query)

    if not found:
        lines.append("❌ No songs found. Cannot create empty playlist.")
        return [TextContent(type="text", text="\n".join(lines))]

    try:
        playlist_id = yt.create_playlist(title=title, description=description, privacy_status=privacy_status)
        video_ids = [item["song"]["videoId"] for item in found]
        yt.add_playlist_items(playlist_id, video_ids)
        _cache_invalidate("library_playlists")  # invalidate cache
        lines.append(f"✅ **Playlist created!** ID: `{playlist_id}`\n")
        lines.append(f"**Added {len(found)} songs:**")
        for i, item in enumerate(found, 1):
            song = item["song"]
            artists = song.get("artists") or []
            artist = _artist_name(artists[0]) if artists else "Unknown"
            lines.append(f"{i}. **{song.get('title','?')}** — {artist}  _(searched: \"{item['query']}\")_")
    except Exception as exc:
        raise PlaylistError(f"Failed to create playlist: {exc}") from exc

    if not_found:
        lines.append(f"\n❌ **Not found ({len(not_found)}):**")
        for q in not_found:
            lines.append(f"  • \"{q}\"")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_list_playlists(limit: int = 25) -> list[TextContent]:
    playlists = _get_library_playlists_cached()
    if not playlists:
        return [TextContent(type="text", text="📝 No playlists found in your library.")]

    shown = playlists[:limit]
    lines = [f"## 📝 Your Playlists ({len(playlists):,} total)\n"]
    for i, pl in enumerate(shown, 1):
        name = pl.get("title", "Unnamed")
        count = pl.get("count", "?")
        pl_id = pl.get("playlistId", "")
        lines.append(f"{i}. **{name}** — {count} songs  `{pl_id}`")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_get_playlist_songs(playlist_id: str, limit: int = 50) -> list[TextContent]:
    yt = get_yt()
    playlist = yt.get_playlist(playlist_id, limit=limit)
    pl_title = playlist.get("title", "Playlist")
    tracks = playlist.get("tracks", [])

    lines = [f"## 📝 {pl_title}\n_{len(tracks)} songs shown_\n"]
    for i, track in enumerate(tracks, 1):
        lines.append(_fmt_song(track, i))

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_add_songs_to_playlist(playlist_id: str, song_queries: list[str]) -> list[TextContent]:
    yt = get_yt()
    found, not_found = [], []

    for query in song_queries:
        try:
            results = yt.search(query, filter="songs", limit=1)
            song = next((r for r in results if r.get("resultType") == "song"), None)
            if song and song.get("videoId"):
                found.append({"query": query, "song": song})
            else:
                not_found.append(query)
        except Exception as exc:
            log.warning("Search failed for '%s': %s", query, exc)
            not_found.append(query)

    if not found:
        return [TextContent(type="text", text="❌ No songs found to add.")]

    video_ids = [item["song"]["videoId"] for item in found]
    yt.add_playlist_items(playlist_id, video_ids)

    lines = [f"## ✅ Added {len(found)} songs to playlist `{playlist_id}`\n"]
    for i, item in enumerate(found, 1):
        song = item["song"]
        artists = song.get("artists") or []
        artist = _artist_name(artists[0]) if artists else "Unknown"
        lines.append(f"{i}. **{song.get('title','?')}** — {artist}")

    if not_found:
        lines.append(f"\n❌ Not found ({len(not_found)}): {', '.join(not_found)}")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_build_smart_playlist(
    mood: str,
    genre: str = "",
    energy_level: str = "medium",
    count: int = 15,
    title: str = "",
    save_playlist: bool = False,
) -> list[TextContent]:
    """
    Agentic multi-step playlist builder.
    Step 1: Fetch mood categories from YTMusic.
    Step 2: Match requested mood/genre to a real YTMusic mood category.
    Step 3: Fetch playlist pool from that category.
    Step 4: Pick tracks from pool, filter by energy heuristic.
    Step 5: Optionally save as a new playlist.
    """
    yt = get_yt()
    lines = [f"## 🧠 Smart Playlist Builder\n**Mood:** {mood}  |  **Genre:** {genre or 'Any'}  |  **Energy:** {energy_level}\n"]

    # Step 1 — Fetch mood categories
    lines.append("**Step 1:** Fetching mood & genre categories from YouTube Music…")
    try:
        mood_cats = yt.get_mood_categories()
    except Exception as exc:
        log.warning("get_mood_categories failed: %s", exc)
        mood_cats = {}

    # Step 2 — Match mood keyword
    lines.append("**Step 2:** Matching your mood to YouTube Music categories…")
    matched_params: str | None = None
    matched_label: str = ""
    target = (mood + " " + genre).lower()

    for section, categories in mood_cats.items():
        for cat in categories:
            cat_title = cat.get("title", "").lower()
            if any(word in cat_title for word in target.split() if len(word) > 2):
                matched_params = cat.get("params")
                matched_label = cat.get("title", "")
                break
        if matched_params:
            break

    if not matched_params:
        # Fallback: just search for mood directly
        lines.append(f"  → No exact category match; using search fallback for **\"{mood}\"**")
        try:
            results = yt.search(f"{mood} {genre} music playlist".strip(), filter="playlists", limit=5)
            playlist_pool = results[:3]
        except Exception:
            playlist_pool = []
    else:
        lines.append(f"  → Matched category: **{matched_label}**")
        # Step 3 — Fetch mood playlists
        lines.append("**Step 3:** Fetching playlists for that mood category…")
        try:
            playlist_pool = yt.get_mood_playlists(matched_params)[:5]
        except Exception as exc:
            log.warning("get_mood_playlists failed: %s", exc)
            playlist_pool = []

    # Step 4 — Gather tracks from playlists
    lines.append("**Step 4:** Sampling tracks from mood playlists…")
    all_tracks: list[dict] = []
    seen_vids: set[str] = set()

    for pl in playlist_pool:
        pl_id = pl.get("playlistId") or pl.get("browseId", "")
        if not pl_id:
            continue
        try:
            pl_data = yt.get_playlist(pl_id, limit=30)
            for track in pl_data.get("tracks", []):
                vid = track.get("videoId")
                if vid and vid not in seen_vids:
                    seen_vids.add(vid)
                    all_tracks.append(track)
                if len(all_tracks) >= count * 3:
                    break
        except Exception:
            continue
        if len(all_tracks) >= count * 3:
            break

    # Energy heuristic — short tracks = high energy, long = mellow
    energy_filter: list[dict] = []
    for track in all_tracks:
        dur = track.get("duration_seconds") or 0
        if energy_level == "high" and (dur < 210 or dur == 0):
            energy_filter.append(track)
        elif energy_level == "low" and dur > 240:
            energy_filter.append(track)
        else:
            energy_filter.append(track)  # medium: no filter

    selected = energy_filter[:count]

    lines.append(f"**Step 5:** Selected **{len(selected)}** tracks\n")
    lines.append("### 🎶 Track List\n")
    for i, track in enumerate(selected, 1):
        lines.append(_fmt_song(track, i))

    # Optional save
    if save_playlist and selected:
        lines.append("\n**Step 6:** Creating playlist on YouTube Music…")
        pl_title = title or f"{mood.title()} {genre.title()} Mix".strip()
        pl_desc = f"Smart playlist: {mood} {genre}, {energy_level} energy. Created by YouTube Music MCP."
        try:
            video_ids = [t["videoId"] for t in selected if t.get("videoId")]
            pl_id = yt.create_playlist(title=pl_title, description=pl_desc, privacy_status="PRIVATE")
            yt.add_playlist_items(pl_id, video_ids)
            _cache_invalidate("library_playlists")
            lines.append(f"✅ Saved as **\"{pl_title}\"** (ID: `{pl_id}`)")
        except Exception as exc:
            lines.append(f"❌ Could not save playlist: {exc}")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_explore_moods() -> list[TextContent]:
    """Fetch all available mood & genre categories from YouTube Music."""
    yt = get_yt()
    try:
        mood_cats = yt.get_mood_categories()
    except Exception as exc:
        raise SearchError(f"Could not fetch mood categories: {exc}") from exc

    lines = ["## 🎨 YouTube Music — Moods & Genres\n"]
    for section, categories in mood_cats.items():
        lines.append(f"### {section}")
        for cat in categories:
            lines.append(f"  • **{cat.get('title', 'Unknown')}**")
        lines.append("")

    lines.append("_Use `build_smart_playlist` with any mood/genre name above._")
    return [TextContent(type="text", text="\n".join(lines))]


async def tool_get_charts(country: str = "ZZ") -> list[TextContent]:
    """Get global or country-specific music charts."""
    yt = get_yt()
    try:
        charts = yt.get_charts(country=country)
    except Exception as exc:
        raise SearchError(f"Could not fetch charts: {exc}") from exc

    lines = [f"## 📈 YouTube Music Charts {'(Global)' if country == 'ZZ' else f'({country})'}\n"]

    # Videos / trending songs
    videos = charts.get("videos", {})
    if videos:
        items = videos.get("items", [])[:10]
        lines.append("### 🔥 Trending Songs")
        for i, v in enumerate(items, 1):
            title = v.get("title", "Unknown")
            artists = v.get("artists") or []
            artist = _artist_name(artists[0]) if artists else "Unknown"
            lines.append(f"{i}. **{title}** — {artist}")
        lines.append("")

    # Artists
    artists = charts.get("artists", {})
    if artists:
        items = artists.get("items", [])[:10]
        lines.append("### 🎤 Trending Artists")
        for i, a in enumerate(items, 1):
            name = a.get("title", "Unknown")
            lines.append(f"{i}. {name}")
        lines.append("")

    if len(lines) == 2:
        lines.append("_No chart data available for this region._")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_get_listening_insights() -> list[TextContent]:
    """Analyze listening history to surface patterns and insights."""
    yt = get_yt()

    try:
        history = yt.get_history()
    except Exception as exc:
        return [TextContent(type="text", text=f"⚠️ Could not fetch history: {exc}\n_History requires authentication._")]

    if not history:
        return [TextContent(type="text", text="📊 No listening history found.")]

    # Analyze
    artist_counts: Counter = Counter()
    album_counts: Counter = Counter()
    title_words: Counter = Counter()

    for track in history:
        artists = track.get("artists") or []
        if artists:
            artist_counts[_artist_name(artists[0])] += 1
        album_obj = track.get("album") or {}
        album = album_obj.get("name", "") if isinstance(album_obj, dict) else ""
        if album:
            album_counts[album] += 1
        title = track.get("title", "")
        for word in title.lower().split():
            if len(word) > 4:
                title_words[word] += 1

    total = len(history)
    top_artists = artist_counts.most_common(5)
    top_albums = album_counts.most_common(3)

    lines = [
        "## 🔍 Listening Insights",
        f"_Analyzing your {total} most recent tracks_\n",
        "### 🎤 Most Listened Artists (recently)",
    ]
    for artist, cnt in top_artists:
        lines.append(f"  • **{artist}** — {cnt} plays")

    if top_albums:
        lines.append("\n### 💿 Most Listened Albums (recently)")
        for album, cnt in top_albums:
            lines.append(f"  • **{album}** — {cnt} plays")

    # Diversity score
    unique_artists = len(artist_counts)
    diversity = unique_artists / total * 100 if total else 0
    mood_word = "varied" if diversity > 50 else ("balanced" if diversity > 25 else "focused")
    lines.append("\n### 📊 Listening Profile")
    lines.append(f"  • **Diversity score:** {diversity:.0f}% ({mood_word} taste)")
    lines.append(f"  • **Unique artists:** {unique_artists} out of {total} recent plays")

    # Repeat listener insight
    repeat_artist = top_artists[0][0] if top_artists else "N/A"
    repeat_cnt = top_artists[0][1] if top_artists else 0
    if repeat_cnt > total * 0.2:
        lines.append(f"\n💡 **Insight:** You're in a **{repeat_artist}** phase right now — {repeat_cnt} of your last {total} plays!")
    else:
        lines.append(f"\n💡 **Insight:** Your recent listening is eclectic — you've spread plays across {unique_artists} artists.")

    return [TextContent(type="text", text="\n".join(lines))]


async def tool_get_server_info() -> list[TextContent]:
    cached_songs = _cache_get("library_songs")
    lib_size = f"{len(cached_songs):,}" if cached_songs else "not cached"
    cached_pls = _cache_get("library_playlists")
    pl_size = f"{len(cached_pls):,}" if cached_pls else "not cached"

    lines = [
        "## ⚙️ YouTube Music MCP Server\n",
        "**Version:** 2.0.0",
        f"**Auth method:** `{_auth_method}`",
        f"**ytmusicapi version:** {ytmusicapi.__version__}",
        f"**Cache TTL:** {CACHE_TTL}s",
        f"**Library songs (cache):** {lib_size}",
        f"**Playlists (cache):** {pl_size}",
        "",
        "**Capabilities:**",
        "  • 15 Tools  |  3 Resources  |  3 Prompts",
        "  • Async parallel search  |  TTL caching",
        "  • Real YTMusic radio similarity engine",
        "  • Mood & genre explorer  |  Charts  |  Insights",
    ]
    return [TextContent(type="text", text="\n".join(lines))]


# ─────────────────────────────────────────────
# MCP Server Setup
# ─────────────────────────────────────────────
app = Server("youtube-music-server")

# ── Tools ──────────────────────────────────────

TOOLS: list[Tool] = [
    Tool(
        name="get_liked_songs_count",
        description="Get the total count of songs in your YouTube Music library (bypasses display limit).",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_library_stats",
        description="Comprehensive library statistics: total songs, unique artists, playlists, and optional top-artist breakdown.",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Include detailed breakdown (top artists, avg songs per artist)",
                    "default": False,
                }
            },
            "required": [],
        },
    ),
    Tool(
        name="search_music",
        description="Search YouTube Music for songs, albums, artists, playlists, or videos.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "filter_type": {
                    "type": "string",
                    "description": "Filter results by type",
                    "enum": ["all", "songs", "albums", "artists", "playlists", "videos"],
                    "default": "all",
                },
                "limit": {"type": "number", "description": "Max results", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_top_artists",
        description="Get your top artists ranked by song count in your library, with visual progress bars.",
        inputSchema={
            "type": "object",
            "properties": {"limit": {"type": "number", "description": "Number of artists", "default": 10}},
            "required": [],
        },
    ),
    Tool(
        name="find_similar_songs",
        description="Find songs genuinely similar to a given track using YouTube Music's real radio engine.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Song name or 'artist - song'"},
                "limit": {"type": "number", "description": "Number of similar songs", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="get_recommendations",
        description="Get personalized recommendations based on your top 5 library artists, fetched in parallel.",
        inputSchema={
            "type": "object",
            "properties": {"count": {"type": "number", "description": "Number of recommendations", "default": 20}},
            "required": [],
        },
    ),
    Tool(
        name="create_playlist_from_songs",
        description="Create a new YouTube Music playlist and add songs to it by search query.",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Playlist title"},
                "song_queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of song search queries",
                },
                "description": {"type": "string", "description": "Playlist description", "default": ""},
                "privacy_status": {
                    "type": "string",
                    "enum": ["PRIVATE", "PUBLIC", "UNLISTED"],
                    "default": "PRIVATE",
                },
            },
            "required": ["title", "song_queries"],
        },
    ),
    Tool(
        name="list_playlists",
        description="List all playlists in your YouTube Music library with song counts and IDs.",
        inputSchema={
            "type": "object",
            "properties": {"limit": {"type": "number", "description": "Max playlists to show", "default": 25}},
            "required": [],
        },
    ),
    Tool(
        name="get_playlist_songs",
        description="Get the songs in a specific playlist by playlist ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "playlist_id": {"type": "string", "description": "Playlist ID (from list_playlists)"},
                "limit": {"type": "number", "description": "Max songs to return", "default": 50},
            },
            "required": ["playlist_id"],
        },
    ),
    Tool(
        name="add_songs_to_playlist",
        description="Add songs to an existing playlist by search queries.",
        inputSchema={
            "type": "object",
            "properties": {
                "playlist_id": {"type": "string", "description": "Target playlist ID"},
                "song_queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Songs to search and add",
                },
            },
            "required": ["playlist_id", "song_queries"],
        },
    ),
    Tool(
        name="build_smart_playlist",
        description=(
            "Agentic multi-step playlist builder. Matches your mood/genre to real YouTube Music categories, "
            "samples tracks, applies energy filtering, and optionally saves as a playlist. "
            "Steps: fetch categories → match mood → pull playlists → sample tracks → energy filter → (optional) save."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "mood": {"type": "string", "description": "Mood or vibe (e.g. 'chill', 'workout', 'focus', 'sad', 'happy')"},
                "genre": {"type": "string", "description": "Optional genre (e.g. 'pop', 'hip-hop', 'jazz')", "default": ""},
                "energy_level": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Energy level filter",
                    "default": "medium",
                },
                "count": {"type": "number", "description": "Number of tracks to include", "default": 15},
                "title": {"type": "string", "description": "Custom playlist title (optional)", "default": ""},
                "save_playlist": {
                    "type": "boolean",
                    "description": "Save the result as a new YouTube Music playlist",
                    "default": False,
                },
            },
            "required": ["mood"],
        },
    ),
    Tool(
        name="explore_moods",
        description="Discover all available Moods & Genres categories on YouTube Music. Use these with build_smart_playlist.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_charts",
        description="Get global or country-specific music charts from YouTube Music (trending songs and artists).",
        inputSchema={
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "ISO 3166-1 Alpha-2 country code (e.g. 'US', 'GB', 'IN'). Default 'ZZ' = global.",
                    "default": "ZZ",
                }
            },
            "required": [],
        },
    ),
    Tool(
        name="get_listening_insights",
        description="Analyze your listening history to surface patterns: top recent artists, albums, diversity score, and behavioural insights.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
    Tool(
        name="get_server_info",
        description="Get metadata about this MCP server: auth method, version, cache state, and capabilities.",
        inputSchema={"type": "object", "properties": {}, "required": []},
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    log.info("Tool called: %s  args=%s", name, list((arguments or {}).keys()))
    args = arguments or {}
    try:
        match name:
            case "get_liked_songs_count":
                return await tool_get_liked_songs_count()
            case "get_library_stats":
                return await tool_get_library_stats(args.get("detailed", False))
            case "search_music":
                if not args.get("query"):
                    raise ValueError("query is required")
                return await tool_search_music(args["query"], args.get("filter_type", "all"), args.get("limit", 10))
            case "get_top_artists":
                return await tool_get_top_artists(args.get("limit", 10))
            case "find_similar_songs":
                if not args.get("query"):
                    raise ValueError("query is required")
                return await tool_find_similar_songs(args["query"], args.get("limit", 10))
            case "get_recommendations":
                return await tool_get_recommendations(args.get("count", 20))
            case "create_playlist_from_songs":
                if not args.get("title"):
                    raise ValueError("title is required")
                if not isinstance(args.get("song_queries"), list):
                    raise ValueError("song_queries must be a list")
                return await tool_create_playlist_from_songs(
                    args["title"], args["song_queries"],
                    args.get("description", ""), args.get("privacy_status", "PRIVATE"),
                )
            case "list_playlists":
                return await tool_list_playlists(args.get("limit", 25))
            case "get_playlist_songs":
                if not args.get("playlist_id"):
                    raise ValueError("playlist_id is required")
                return await tool_get_playlist_songs(args["playlist_id"], args.get("limit", 50))
            case "add_songs_to_playlist":
                if not args.get("playlist_id"):
                    raise ValueError("playlist_id is required")
                if not isinstance(args.get("song_queries"), list):
                    raise ValueError("song_queries must be a list")
                return await tool_add_songs_to_playlist(args["playlist_id"], args["song_queries"])
            case "build_smart_playlist":
                if not args.get("mood"):
                    raise ValueError("mood is required")
                return await tool_build_smart_playlist(
                    args["mood"], args.get("genre", ""), args.get("energy_level", "medium"),
                    args.get("count", 15), args.get("title", ""), args.get("save_playlist", False),
                )
            case "explore_moods":
                return await tool_explore_moods()
            case "get_charts":
                return await tool_get_charts(args.get("country", "ZZ"))
            case "get_listening_insights":
                return await tool_get_listening_insights()
            case "get_server_info":
                return await tool_get_server_info()
            case _:
                raise ValueError(f"Unknown tool: {name}")

    except (AuthError, SearchError, PlaylistError) as exc:
        log.error("Domain error in %s: %s", name, exc)
        return [TextContent(type="text", text=f"❌ **{type(exc).__name__}:** {exc}")]
    except ValueError as exc:
        return [TextContent(type="text", text=f"⚠️ **Invalid input:** {exc}")]
    except Exception as exc:
        log.exception("Unexpected error in tool %s", name)
        return [TextContent(type="text", text=f"❌ **Unexpected error in `{name}`:** {exc}")]


# ── Resources ──────────────────────────────────

RESOURCES: list[Resource] = [
    Resource(
        uri="library://songs",  # type: ignore[arg-type]
        name="Liked Songs Library",
        description="All songs in your YouTube Music library as structured JSON. Cached for 5 minutes.",
        mimeType="application/json",
    ),
    Resource(
        uri="library://artists",  # type: ignore[arg-type]
        name="Artist Rankings",
        description="Your top artists ranked by song count as structured JSON.",
        mimeType="application/json",
    ),
    Resource(
        uri="library://playlists",  # type: ignore[arg-type]
        name="Playlists",
        description="All your YouTube Music playlists as structured JSON.",
        mimeType="application/json",
    ),
]


@app.list_resources()
async def list_resources() -> list[Resource]:
    return RESOURCES


@app.read_resource()
async def read_resource(uri: Any) -> ReadResourceResult:
    uri_str = str(uri)
    log.info("Resource read: %s", uri_str)

    if uri_str == "library://songs":
        songs = _get_library_songs_cached()
        data = [
            {
                "title": s.get("title"),
                "artist": _artist_name((s.get("artists") or [{}])[0]),
                "album": (s.get("album") or {}).get("name"),
                "videoId": s.get("videoId"),
            }
            for s in songs
        ]
        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps(data, indent=2))]
        )

    elif uri_str == "library://artists":
        songs = _get_library_songs_cached()
        counts = _artist_counts(songs)
        total = len(songs)
        data = [
            {"rank": i, "artist": a, "songs": c, "percentage": round(c / total * 100, 1)}
            for i, (a, c) in enumerate(counts.most_common(50), 1)
        ]
        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps(data, indent=2))]
        )

    elif uri_str == "library://playlists":
        playlists = _get_library_playlists_cached()
        data = [
            {"title": p.get("title"), "playlistId": p.get("playlistId"), "count": p.get("count")}
            for p in playlists
        ]
        return ReadResourceResult(
            contents=[TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps(data, indent=2))]
        )

    else:
        raise ValueError(f"Unknown resource URI: {uri_str}")


# ── Prompts ────────────────────────────────────

PROMPTS: list[Prompt] = [
    Prompt(
        name="weekly-discovery-mix",
        description="Generate a personalised weekly discovery playlist conversation starter. Analyses your library and suggests an exploration strategy.",
        arguments=[
            PromptArgument(name="discovery_style", description="'familiar' (artist adjacents) or 'adventurous' (new genres)", required=False),
        ],
    ),
    Prompt(
        name="mood-based-playlist",
        description="Build a mood-based playlist through a guided conversation. Asks about mood, energy, and context.",
        arguments=[
            PromptArgument(name="mood", description="Starting mood (e.g. chill, energetic, focus, sad)", required=True),
            PromptArgument(name="duration_minutes", description="Desired playlist duration in minutes", required=False),
        ],
    ),
    Prompt(
        name="artist-deep-dive",
        description="Deep dive into a specific artist: explore their discography, find similar artists, and build a comprehensive listening experience.",
        arguments=[
            PromptArgument(name="artist_name", description="Artist to explore", required=True),
        ],
    ),
]


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return PROMPTS


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    args = arguments or {}
    log.info("Prompt requested: %s  args=%s", name, args)

    if name == "weekly-discovery-mix":
        style = args.get("discovery_style", "familiar")
        style_desc = (
            "Lean towards artists similar to what's already in my library — adjacent but slightly new."
            if style == "familiar"
            else "Push me outside my comfort zone — completely new genres and artists I've never heard."
        )
        return GetPromptResult(
            description="Weekly discovery mix prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"I want to create my weekly discovery mix. Style: {style} ({style_desc})\n\n"
                            "Please:\n"
                            "1. Use `get_library_stats` (detailed=true) to understand my library\n"
                            "2. Use `get_top_artists` to see who I listen to most\n"
                            "3. Use `get_recommendations` to get a seed list\n"
                            "4. Use `find_similar_songs` on 2-3 of my favourite tracks\n"
                            "5. Compile a 20-song Weekly Discovery Mix playlist\n"
                            "6. Use `create_playlist_from_songs` to save it as 'Weekly Discovery — [date]'\n\n"
                            "Show me each step's reasoning as you go."
                        ),
                    ),
                )
            ],
        )

    elif name == "mood-based-playlist":
        mood = args.get("mood", "chill")
        duration = args.get("duration_minutes", "30")
        return GetPromptResult(
            description="Mood-based playlist builder prompt",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"I'm in a **{mood}** mood and want a ~{duration} minute playlist.\n\n"
                            "Please:\n"
                            "1. Use `explore_moods` to find matching YouTube Music mood categories\n"
                            f"2. Use `build_smart_playlist` with mood='{mood}' to generate a track list\n"
                            "3. Cross-reference with my library using `get_library_stats` — prioritise artists I already love\n"
                            "4. Refine the list and explain why each track fits the mood\n"
                            "5. Ask me if I want to save it as a playlist\n\n"
                            "Be conversational — this is a collaborative music curation session."
                        ),
                    ),
                )
            ],
        )

    elif name == "artist-deep-dive":
        artist = args.get("artist_name", "")
        if not artist:
            raise ValueError("artist_name is required for artist-deep-dive prompt")
        return GetPromptResult(
            description=f"Artist deep dive: {artist}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Let's do a deep dive on **{artist}**.\n\n"
                            "Please:\n"
                            f"1. Use `search_music` (filter_type='songs') to find their top tracks\n"
                            f"2. Use `search_music` (filter_type='albums') to map their discography\n"
                            f"3. Use `find_similar_songs` on their most iconic song to find similar artists\n"
                            "4. Check if any of their songs are in my library using `get_library_stats`\n"
                            "5. Give me a curated listening plan: 'Start here → then this → then explore'\n"
                            f"6. Create a '{artist} Deep Dive' playlist with their essential tracks\n\n"
                            "I want to understand their artistry, not just list songs."
                        ),
                    ),
                )
            ],
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
async def main() -> None:
    log.info("Starting YouTube Music MCP Server v2.0.0")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
