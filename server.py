#!/usr/bin/env python3
"""
YouTube Music MCP Server

A Model Context Protocol server that provides AI assistants with access to YouTube Music.
Implements 7 tools for music discovery, library management, and recommendations.
"""

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from ytmusicapi import YTMusic

# Global YTMusic instance
ytmusic: YTMusic | None = None


def initialize_ytmusic() -> YTMusic:
    """
    Initialize YouTube Music API with authentication.
    Supports both OAuth and browser authentication.
    """
    global ytmusic
    
    if ytmusic is not None:
        return ytmusic
    
    # Try OAuth first (recommended)
    oauth_path = Path("oauth.json")
    browser_path = Path("browser.json")
    
    try:
        if oauth_path.exists():
            ytmusic = YTMusic(str(oauth_path))
        elif browser_path.exists():
            ytmusic = YTMusic(str(browser_path))
        else:
            raise FileNotFoundError(
                "No authentication file found. Please create either oauth.json or browser.json. "
                "See README.md for setup instructions."
            )
        return ytmusic
        
    except Exception as e:
        raise


def get_artist_name(artist: str | dict) -> str:
    """Extract artist name from various formats."""
    if isinstance(artist, str):
        return artist
    elif isinstance(artist, dict):
        return artist.get("name", "Unknown Artist")
    return "Unknown Artist"


async def handle_get_liked_songs_count() -> list[TextContent]:
    """
    Tool 1: Get total count of liked songs in library.
    Bypasses YouTube's display limit.
    """
    yt = initialize_ytmusic()
    songs = yt.get_library_songs(limit=None)
    count = len(songs)
    
    return [
        TextContent(
            type="text",
            text=f"🎵 You have **{count:,}** songs in your YouTube Music library!"
        )
    ]


async def handle_get_library_stats(detailed: bool = False) -> list[TextContent]:
    """
    Tool 2: Get comprehensive library statistics.
    """
    yt = initialize_ytmusic()
    songs = yt.get_library_songs(limit=None)
    total_songs = len(songs)
    
    # Count unique artists
    artists = set()
    for song in songs:
        if "artists" in song and song["artists"]:
            artist_name = get_artist_name(song["artists"][0])
            artists.add(artist_name)
    
    unique_artists = len(artists)
    
    response = "📊 **Library Statistics**\n\n"
    response += f"🎵 Total Songs: **{total_songs:,}**\n"
    response += f"🎤 Unique Artists: **{unique_artists:,}**\n"
    
    if detailed and total_songs > 0:
        avg_songs_per_artist = total_songs / unique_artists if unique_artists > 0 else 0
        response += f"📈 Average Songs per Artist: **{avg_songs_per_artist:.1f}**\n"
    
    return [TextContent(type="text", text=response)]


async def handle_search_music(query: str, limit: int = 10) -> list[TextContent]:
    """
    Tool 3: Search for music on YouTube Music.
    """
    yt = initialize_ytmusic()
    results = yt.search(query, limit=limit)
    
    if not results:
        return [TextContent(type="text", text=f"🔍 No results found for \"{query}\"")]
    
    response = f"🔍 **Search Results for \"{query}\"**\n\n"
    
    # Group by type
    by_type: dict[str, list[dict]] = {}
    for item in results:
        result_type = item.get("resultType", "other")
        if result_type not in by_type:
            by_type[result_type] = []
        by_type[result_type].append(item)
    
    # Format each type
    for result_type, items in by_type.items():
        if result_type == "song":
            response += "**🎵 Songs:**\n"
            for idx, song in enumerate(items, 1):
                title = song.get("title", "Unknown")
                artists = song.get("artists", [])
                artist_name = get_artist_name(artists[0]) if artists else "Unknown Artist"
                album = song.get("album", {}).get("name", "Unknown Album") if song.get("album") else "Unknown Album"
                response += f"{idx}. \"{title}\" by {artist_name}\n"
                response += f"   Album: {album}\n"
            response += "\n"
            
        elif result_type == "album":
            response += "**💿 Albums:**\n"
            for idx, album in enumerate(items, 1):
                title = album.get("title", "Unknown")
                artists = album.get("artists", [])
                artist_name = get_artist_name(artists[0]) if artists else "Unknown Artist"
                response += f"{idx}. \"{title}\" by {artist_name}\n"
            response += "\n"
            
        elif result_type == "artist":
            response += "**🎤 Artists:**\n"
            for idx, artist in enumerate(items, 1):
                name = artist.get("artist", "Unknown")
                response += f"{idx}. {name}\n"
            response += "\n"
            
        elif result_type == "playlist":
            response += "**📝 Playlists:**\n"
            for idx, playlist in enumerate(items, 1):
                title = playlist.get("title", "Unknown")
                response += f"{idx}. \"{title}\"\n"
            response += "\n"
            
        elif result_type == "video":
            response += "**🎬 Videos:**\n"
            for idx, video in enumerate(items, 1):
                title = video.get("title", "Unknown")
                artists = video.get("artists", [])
                artist_name = get_artist_name(artists[0]) if artists else "Unknown Artist"
                response += f"{idx}. \"{title}\" by {artist_name}\n"
            response += "\n"
    
    return [TextContent(type="text", text=response)]


async def handle_get_top_artists(limit: int = 10) -> list[TextContent]:
    """
    Tool 4: Get top artists from library ranked by song count.
    """
    yt = initialize_ytmusic()
    songs = yt.get_library_songs(limit=None)
    
    if not songs:
        return [TextContent(type="text", text="📊 Your library is empty. Add some songs first!")]
    
    # Count artist occurrences
    artist_counts: Counter = Counter()
    for song in songs:
        if "artists" in song and song["artists"]:
            artist_name = get_artist_name(song["artists"][0])
            artist_counts[artist_name] += 1
    
    # Get top artists
    top_artists = artist_counts.most_common(limit)
    total_songs = len(songs)
    
    response = f"🎤 **Top {min(limit, len(top_artists))} Artists in Your Library**\n\n"
    
    for idx, (artist, count) in enumerate(top_artists, 1):
        percentage = (count / total_songs * 100) if total_songs > 0 else 0
        response += f"{idx}. **{artist}**\n"
        response += f"   {count:,} songs ({percentage:.1f}% of library)\n\n"
    
    return [TextContent(type="text", text=response)]


async def handle_find_similar_songs(query: str, limit: int = 10) -> list[TextContent]:
    """
    Tool 5: Find songs similar to a given song.
    """
    yt = initialize_ytmusic()
    
    # Search for the seed song
    search_results = yt.search(query, limit=5)
    seed_song = next((r for r in search_results if r.get("resultType") == "song"), None)
    
    if not seed_song:
        return [TextContent(
            type="text",
            text=f"🔍 Couldn't find a song matching \"{query}\". Try a different search term."
        )]
    
    song_title = seed_song.get("title", "Unknown")
    artists = seed_song.get("artists", [])
    artist_name = get_artist_name(artists[0]) if artists else None
    
    if not artist_name:
        return [TextContent(
            type="text",
            text=f"❌ Couldn't determine the artist for \"{song_title}\"."
        )]
    
    # Search for more songs by the same artist
    artist_results = yt.search(artist_name, limit=limit + 5)
    similar_songs = [
        r for r in artist_results
        if r.get("resultType") == "song" and r.get("videoId") != seed_song.get("videoId")
    ][:limit]
    
    response = f"🎵 **Songs Similar to \"{song_title}\" by {artist_name}**\n\n"
    
    if not similar_songs:
        response += "No similar songs found. Try searching for the artist directly."
    else:
        for idx, song in enumerate(similar_songs, 1):
            title = song.get("title", "Unknown")
            album = song.get("album", {}).get("name", "Unknown Album") if song.get("album") else "Unknown Album"
            response += f"{idx}. \"{title}\"\n"
            response += f"   Album: {album}\n\n"
    
    return [TextContent(type="text", text=response)]


async def handle_get_recommendations(count: int = 20) -> list[TextContent]:
    """
    Tool 6: Get personalized recommendations based on library.
    """
    yt = initialize_ytmusic()
    songs = yt.get_library_songs(limit=None)
    
    if not songs:
        return [TextContent(
            type="text",
            text="📊 Your library is empty. Add some songs to get personalized recommendations!"
        )]
    
    # Count artist occurrences to find top artists
    artist_counts: Counter = Counter()
    for song in songs:
        if "artists" in song and song["artists"]:
            artist_name = get_artist_name(song["artists"][0])
            artist_counts[artist_name] += 1
    
    # Get top 3 artists
    top_artists = [artist for artist, _ in artist_counts.most_common(3)]
    
    if not top_artists:
        return [TextContent(
            type="text",
            text="❌ Could not determine your top artists. Please ensure your library has artist information."
        )]
    
    # Search for songs from top artists
    recommendations = []
    seen_video_ids = set()
    
    for artist in top_artists:
        try:
            results = yt.search(artist, limit=15)
            artist_songs = [r for r in results if r.get("resultType") == "song"]
            
            for song in artist_songs:
                video_id = song.get("videoId")
                if video_id and video_id not in seen_video_ids:
                    recommendations.append(song)
                    seen_video_ids.add(video_id)
                    
                    if len(recommendations) >= count:
                        break
            
            if len(recommendations) >= count:
                break
        except Exception as e:
            print(f"Error searching for artist {artist}: {e}", flush=True)
            continue
    
    response = "✨ **Personalized Recommendations** (based on your top artists)\n\n"
    response += f"Top artists: {', '.join(top_artists)}\n\n"
    
    if not recommendations:
        response += "No recommendations found. Try adding more songs to your library."
    else:
        for idx, song in enumerate(recommendations, 1):
            title = song.get("title", "Unknown")
            artists = song.get("artists", [])
            artist_name = get_artist_name(artists[0]) if artists else "Unknown Artist"
            album = song.get("album", {}).get("name", "Unknown Album") if song.get("album") else "Unknown Album"
            response += f"{idx}. \"{title}\" by {artist_name}\n"
            response += f"   Album: {album}\n\n"
    
    return [TextContent(type="text", text=response)]


async def handle_create_playlist_from_songs(
    title: str, 
    song_queries: list[str], 
    description: str = "",
    privacy_status: str = "PRIVATE"
) -> list[TextContent]:
    """
    Tool 7: Create playlist and add songs to it.
    """
    yt = initialize_ytmusic()
    
    response = f"📝 **Creating Playlist: \"{title}\"**\n"
    if description:
        response += f"Description: {description}\n"
    response += f"\n"
    
    # Search for songs and collect video IDs
    found_songs = []
    not_found = []
    
    for query in song_queries:
        try:
            results = yt.search(query, limit=1)
            song = next((r for r in results if r.get("resultType") == "song"), None)
            
            if song and song.get("videoId"):
                found_songs.append({
                    "query": query,
                    "song": song
                })
            else:
                not_found.append(query)
        except Exception as e:
            print(f"Error searching for '{query}': {e}", flush=True)
            not_found.append(query)
    
    # Create the playlist
    if found_songs:
        try:
            playlist_id = yt.create_playlist(
                title=title,
                description=description,
                privacy_status=privacy_status
            )
            
            # Add songs to playlist
            video_ids = [song["song"]["videoId"] for song in found_songs]
            yt.add_playlist_items(playlist_id, video_ids)
            
            response += f"✅ **Playlist created successfully!**\n"
            response += f"Playlist ID: {playlist_id}\n\n"
            
            response += f"**✅ Added {len(found_songs)} songs:**\n\n"
            for idx, item in enumerate(found_songs, 1):
                song = item["song"]
                title_text = song.get("title", "Unknown")
                artists = song.get("artists", [])
                artist_name = get_artist_name(artists[0]) if artists else "Unknown Artist"
                album = song.get("album", {}).get("name", "Unknown Album") if song.get("album") else "Unknown Album"
                response += f"{idx}. \"{title_text}\" by {artist_name}\n"
                response += f"   Album: {album}\n"
                response += f"   (searched for: \"{item['query']}\")\n\n"
        except Exception as e:
            response += f"❌ Failed to create playlist: {e}\n\n"
            response += f"**Songs that were found:**\n\n"
            for idx, item in enumerate(found_songs, 1):
                song = item["song"]
                response += f"{idx}. \"{song.get('title', 'Unknown')}\" (searched for: \"{item['query']}\")\n"
    else:
        response += "❌ No songs found. Cannot create empty playlist.\n\n"
    
    # Report not found songs
    if not_found:
        response += f"\n**❌ Not found ({len(not_found)} queries):**\n\n"
        for idx, query in enumerate(not_found, 1):
            response += f"{idx}. \"{query}\"\n"
    
    return [TextContent(type="text", text=response)]


# Create MCP server
app = Server("youtube-music-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_liked_songs_count",
            description="Get the total count of songs in your YouTube Music library. "
                       "This bypasses YouTube's display limit and returns the actual count.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_library_stats",
            description="Get comprehensive statistics about your YouTube Music library, including "
                       "total songs, unique artists, and optional detailed metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed statistics like average songs per artist",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_music",
            description="Search for songs, albums, artists, playlists, or videos on YouTube Music. "
                       "Returns formatted results grouped by type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (song name, artist, album, etc.)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_top_artists",
            description="Get your top artists ranked by the number of songs in your library. "
                       "Shows song counts and percentage of your library for each artist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of top artists to return",
                        "default": 10
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="find_similar_songs",
            description="Find songs similar to a given song. Searches for the song you specify and "
                       "returns other songs by the same artist.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Song name or artist to find similar songs for"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of similar songs to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_recommendations",
            description="Get personalized song recommendations based on your library. "
                       "Analyzes your top artists and suggests songs you might like.",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {
                        "type": "number",
                        "description": "Number of recommendations to return",
                        "default": 20
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="create_playlist_from_songs",
            description="Create a new playlist and add songs to it. Searches for each song and adds them "
                       "to a newly created playlist. Returns detailed report of what was added.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title for the playlist"
                    },
                    "song_queries": {
                        "type": "array",
                        "description": "Array of song search queries (song names, 'artist - song', etc.)",
                        "items": {
                            "type": "string"
                        }
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the playlist",
                        "default": ""
                    },
                    "privacy_status": {
                        "type": "string",
                        "description": "Privacy status: PRIVATE, PUBLIC, or UNLISTED",
                        "enum": ["PRIVATE", "PUBLIC", "UNLISTED"],
                        "default": "PRIVATE"
                    }
                },
                "required": ["title", "song_queries"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""
    try:
        if name == "get_liked_songs_count":
            return await handle_get_liked_songs_count()
        
        elif name == "get_library_stats":
            detailed = arguments.get("detailed", False)
            return await handle_get_library_stats(detailed)
        
        elif name == "search_music":
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            if not query:
                raise ValueError("query parameter is required")
            return await handle_search_music(query, limit)
        
        elif name == "get_top_artists":
            limit = arguments.get("limit", 10)
            return await handle_get_top_artists(limit)
        
        elif name == "find_similar_songs":
            query = arguments.get("query")
            limit = arguments.get("limit", 10)
            if not query:
                raise ValueError("query parameter is required")
            return await handle_find_similar_songs(query, limit)
        
        elif name == "get_recommendations":
            count = arguments.get("count", 20)
            return await handle_get_recommendations(count)
        
        elif name == "create_playlist_from_songs":
            title = arguments.get("title")
            song_queries = arguments.get("song_queries")
            description = arguments.get("description", "")
            privacy_status = arguments.get("privacy_status", "PRIVATE")
            
            if not title:
                raise ValueError("title parameter is required")
            if not song_queries or not isinstance(song_queries, list):
                raise ValueError("song_queries must be a non-empty array")
            
            return await handle_create_playlist_from_songs(
                title, song_queries, description, privacy_status
            )
        
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        error_msg = f"Error executing tool {name}: {str(e)}"
        return [TextContent(type="text", text=f"❌ {error_msg}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
