# YouTube Music MCP Server - Developer Context

This folder contains context information for AI assistants working on this codebase.

## Project Overview

YouTube Music MCP (Model Context Protocol) server that connects YouTube Music to AI assistants like Claude.

## Tech Stack

- **Python 3.10+**
- **ytmusicapi** - YouTube Music API wrapper
- **mcp** - Model Context Protocol SDK
- **asyncio** - Async/await for MCP handlers

## Key Files

- `server.py` - Main MCP server implementation
- `pyproject.toml` - Python dependencies
- `browser.json` - Browser cookie authentication (gitignored)
- `oauth.json` - OAuth authentication (gitignored)
- `update_auth.py` - Simple cookie updater script

## Authentication

Two methods supported:

1. **Browser Cookies** - Expires ~6 months, simpler setup
2. **OAuth** - Auto-refreshing, better for production

Authentication requires SAPISIDHASH header generation from SAPISID cookie.

## MCP Tools Implemented

1. `get_liked_songs_count` - Total liked songs
2. `get_library_stats` - Library statistics
3. `search_music` - Search catalog with filters
4. `get_top_artists` - Top artists from history
5. `find_similar_songs` - Similar track discovery
6. `get_recommendations` - Personalized recommendations
7. `create_playlist_from_songs` - Playlist creation

## Important Notes

- All MCP handlers use async/await
- ytmusic client lazy-initialized on first tool call
- No stdout pollution (MCP protocol compliance)
- Cookie updates needed every 6 months
- SAPISIDHASH must be regenerated for write operations

## Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Test
npx @modelcontextprotocol/inspector venv/bin/python server.py

# Update auth when expired
python update_auth.py
```

## Security

- Never commit browser.json, oauth.json, or cookie.txt
- All sensitive files in .gitignore
- Cookie cleanup after auth update
