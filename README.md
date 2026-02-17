# YouTube Music MCP Server

<div align="center">

A production-grade Model Context Protocol (MCP) server that connects YouTube Music to AI assistants like Claude.  
Implements the full MCP primitive set — **Tools, Resources, and Prompts** — for genuine agentic music experiences.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)
![Tests](https://img.shields.io/badge/tests-51%20passing-brightgreen.svg)
![CI](https://github.com/codeRisshi25/youtubemusic-mcp/actions/workflows/ci.yml/badge.svg)

[Architecture](#architecture) • [Features](#features) • [Installation](#installation) • [Authentication](#authentication) • [Usage](#usage) • [Tools](#tools) • [Resources](#resources) • [Prompts](#prompts)

</div>

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude / AI Assistant                     │
└──────────────────────┬──────────────────────────────────────┘
                       │  Model Context Protocol (stdio)
┌──────────────────────▼──────────────────────────────────────┐
│                 YouTube Music MCP Server v2                  │
│                                                             │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │  15 Tools   │  │  3 Resources  │  │    3 Prompts     │  │
│  │             │  │               │  │                  │  │
│  │ search      │  │library://     │  │weekly-discovery  │  │
│  │ stats       │  │  songs        │  │mood-based-       │  │
│  │ similar ★  │  │  artists      │  │  playlist        │  │
│  │ recommend ★│  │  playlists    │  │artist-deep-dive  │  │
│  │ smart pl ★ │  └───────────────┘  └──────────────────┘  │
│  │ charts      │                                           │
│  │ insights    │  ┌───────────────────────────────────┐    │
│  │ moods       │  │  TTL Cache (5 min)  •  Async ★   │    │
│  │ ...         │  │  Custom Exceptions  •  Logging    │    │
│  └─────────────┘  └───────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │  ytmusicapi
┌──────────────────────▼──────────────────────────────────────┐
│                   YouTube Music API                          │
└─────────────────────────────────────────────────────────────┘
★ = Agentic / async feature
```

---

## Features

**15 Tools · 3 Resources · 3 Prompts — full MCP primitive coverage:**

### 🛠️ Tools
| Tool | Description |
|------|-------------|
| `get_liked_songs_count` | Total song count (bypasses YT display limit) |
| `get_library_stats` | Songs, artists, playlists + detailed breakdown |
| `search_music` | Search with type filter (songs/albums/artists/playlists/videos) |
| `get_top_artists` | Ranked artists with visual progress bars |
| `find_similar_songs` ⭐ | **Real** YTMusic radio engine — not a fake artist search |
| `get_recommendations` ⭐ | Async-parallel fetch across top 5 artists |
| `create_playlist_from_songs` | Create & populate playlist from search queries |
| `list_playlists` | All your playlists with IDs and song counts |
| `get_playlist_songs` | Browse songs in any playlist |
| `add_songs_to_playlist` | Add songs to existing playlist |
| `build_smart_playlist` ⭐ | **Agentic** 6-step pipeline: mood→category→tracks→filter→save |
| `explore_moods` | Discover all YTMusic Moods & Genres categories |
| `get_charts` | Global or country-specific trending charts |
| `get_listening_insights` | History analysis: patterns, diversity score, insights |
| `get_server_info` | Auth method, cache state, version, capabilities |

### 📦 Resources (passively readable by Claude)
| Resource URI | Description |
|---|---|
| `library://songs` | Full library as structured JSON |
| `library://artists` | Artist rankings with percentages |
| `library://playlists` | All playlists as structured JSON |

### 💬 Prompts (guided conversation starters)
| Prompt | Description |
|---|---|
| `weekly-discovery-mix` | Guided weekly music discovery workflow |
| `mood-based-playlist` | Collaborative mood → playlist session |
| `artist-deep-dive` | Full artist exploration + listening plan |

---

## Installation

### Prerequisites

- Python 3.10 or higher
- A YouTube Music account
- Browser developer tools access (for authentication)

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/codeRisshi25/youtubemusic-mcp.git
cd youtubemusic-mcp
```

2. **Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -e .
```

---

## Authentication

Choose one authentication method:

### Option A: Browser Cookies (Recommended)

1. Visit [music.youtube.com](https://music.youtube.com) and log in
2. Open Developer Tools (`F12`)
3. Go to **Network** tab and refresh the page
4. Find any POST request to `music.youtube.com`
5. Right-click → Copy → Copy as cURL
6. Extract the cookie string
7. Run setup:

```bash
python3 -c "
from ytmusicapi import setup
headers_raw = '''PASTE YOUR HEADERS HERE'''
setup(filepath='browser.json', headers_raw=headers_raw)
"
```

**Note:** Cookies may expire after 6-12 months. See [docs/AUTH_UPDATE.md](docs/AUTH_UPDATE.md) for simple update instructions.

### Option B: OAuth (Long-term)

See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) for complete OAuth setup instructions.

---

## Usage

### Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector venv/bin/python server.py
```

Opens web interface at `http://localhost:6274` to test all 15 tools, 3 resources, and 3 prompts.

### Claude Desktop Integration

1. **Config file location:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add configuration:**

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

3. **Restart Claude Desktop**

See [docs/CLAUDE_SETUP.md](docs/CLAUDE_SETUP.md) for detailed instructions.

---

## Available Tools

See the [Features section](#features) above for a full table of all 15 tools.

### Agentic Highlights

**`build_smart_playlist`** — the centrepiece agentic tool. Runs a 6-step pipeline inside a single tool call:
```
Step 1: Fetch all Moods & Genres from YouTube Music
Step 2: Match your mood keyword to a real category
Step 3: Pull mood playlist pool from that category
Step 4: Sample tracks across multiple playlists
Step 5: Apply energy-level filter (high/medium/low)
Step 6: Optionally create & save to YouTube Music
```

**`find_similar_songs`** — uses `get_watch_playlist(radio=True)`, the actual YTMusic similarity engine, not a fake artist search.

**`get_recommendations`** — fetches from 5 artists using `asyncio.gather()` for true parallel execution.

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

51 tests covering auth, caching, all tools, resources, prompts, and routing — no network required (fully mocked).

---

## Troubleshooting

### Authentication Errors

If you get authentication errors after ~6 months:

1. Your cookies have likely expired
2. Follow the simple update process in [docs/AUTH_UPDATE.md](docs/AUTH_UPDATE.md)
3. You'll just need to paste fresh cookies from your browser

### Server Not Detected in Claude

- Use absolute paths in `claude_desktop_config.json`
- Restart Claude Desktop after config changes
- Check logs in Claude → Help → View Logs

### Import Errors

- Ensure virtual environment is activated
- Run `pip install -e .` in the project directory

### Server Crashes on Startup

- Verify `browser.json` or `oauth.json` exists
- Check file permissions
- See [docs/CLAUDE_SETUP.md](docs/CLAUDE_SETUP.md) for detailed troubleshooting

---

## Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

---

## License

MIT License - see [LICENSE](LICENSE)

Copyright (c) 2025 Risshi Raj Sen

---

## Links

- [GitHub Issues](https://github.com/codeRisshi25/youtubemusic-mcp/issues)
- [Discussions](https://github.com/codeRisshi25/youtubemusic-mcp/discussions)

---

<div align="center">

Built with [ytmusicapi](https://github.com/sigma67/ytmusicapi) • [MCP](https://modelcontextprotocol.io/)

⭐ Star if useful!

</div>
