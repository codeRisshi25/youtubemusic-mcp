# YouTube Music MCP Server

<div align="center">

A powerful Model Context Protocol (MCP) server that connects YouTube Music to AI assistants like Claude. Access your music library, get recommendations, search for songs, create playlists, and discover new music through natural language conversations.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)

[Features](#features) • [Installation](#installation) • [Authentication](#authentication) • [Usage](#usage) • [Tools](#available-tools)

</div>

---

## Features

**7 powerful tools for music discovery and library management:**

- 🎵 **get_liked_songs_count** - Get total count of liked songs
- 📊 **get_library_stats** - Comprehensive library statistics (songs, playlists, artists, albums)
- 🔍 **search_music** - Search for songs, artists, albums, or playlists
- 🎤 **get_top_artists** - Most played artists from listening history
- 🎧 **find_similar_songs** - Discover similar tracks
- ✨ **get_recommendations** - Personalized music recommendations
- 📝 **create_playlist_from_songs** - Create playlists from song queries

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

Opens web interface at `http://localhost:6274` to test all tools.

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

| Tool | Description |
|------|-------------|
| `get_liked_songs_count` | Get total count of your liked songs |
| `get_library_stats` | Comprehensive library statistics (songs, playlists, artists, albums) |
| `search_music` | Search for songs, artists, albums, or playlists |
| `get_top_artists` | Get your most played artists from listening history |
| `find_similar_songs` | Discover songs similar to any track |
| `get_recommendations` | Get personalized music recommendations |
| `create_playlist_from_songs` | Create playlists from song queries |

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
