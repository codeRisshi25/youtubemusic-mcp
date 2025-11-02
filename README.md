# YouTube Music MCP Server# 🎵 YouTube Music MCP Server



<div align="center">A powerful Model Context Protocol (MCP) server that connects YouTube Music to AI assistants like Claude. Access your music library, get recommendations, search for songs, create playlists, and discover new music through natural language conversations.



![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)## ✨ Features

![License](https://img.shields.io/badge/license-MIT-green.svg)

![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)This MCP server provides 7 powerful tools:



A powerful Model Context Protocol (MCP) server that gives AI assistants seamless access to YouTube Music. Built with Python and the official ytmusicapi.1. **`get_liked_songs_count`** - Get total count of songs in your library (bypasses YouTube's 5000 display limit)

2. **`get_library_stats`** - Comprehensive library statistics with unique artists and averages

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Tools](#-available-tools) • [Claude Desktop Setup](#-claude-desktop-integration)3. **`search_music`** - Search for songs, albums, artists, playlists, and videos

4. **`get_top_artists`** - Ranked list of your top artists with counts and percentages

</div>5. **`find_similar_songs`** - Discover songs similar to any track

6. **`get_recommendations`** - Personalized recommendations based on your library

---7. **`create_playlist_from_songs`** - Create playlists and automatically add songs to them



## 🎵 Features## 🚀 Quick Start



This production-ready MCP server provides **7 comprehensive tools** for music discovery, library management, and playlist creation:### Prerequisites



### 📊 Library Management- **Python 3.10 or higher**

- **`get_liked_songs_count`** - Get total count of your liked songs- A YouTube Music account with songs in your library

- **`get_library_stats`** - Comprehensive library statistics (songs, playlists, artists, albums)- Access to browser developer tools (for browser authentication) OR ability to set up OAuth



### 🔍 Discovery & Search### Installation

- **`search_music`** - Search for songs, artists, albums, or playlists

- **`get_top_artists`** - Retrieve your most played artists from listening history1. **Clone or download this repository**

- **`find_similar_songs`** - Discover songs similar to any track

- **`get_recommendations`** - Get AI-powered personalized music recommendations```bash

git clone <your-repo-url>

### 🎵 Playlist Managementcd youtube-music-mcp

- **`create_playlist_from_songs`** - Create custom playlists from song queries```



---2. **Install dependencies**



## 📋 Requirements```bash

pip install -e .

- **Python**: 3.10 or higher```

- **YouTube Music**: Active account

- **OS**: Linux, macOS, or WindowsOr if you want development dependencies:



---```bash

pip install -e ".[dev]"

## 🚀 Installation```



### Quick Start3. **Set up authentication** (see detailed instructions below)



1. **Clone the repository**Choose ONE of these methods:

```bash

git clone https://github.com/codeRisshi25/youtubemusic-mcp.git- **OAuth (Recommended)** - More secure, tokens refresh automatically

cd youtubemusic-mcp- **Browser Auth** - Simpler to set up, but requires manual cookie refresh

```

### Authentication Setup

2. **Set up Python environment**

```bash#### Method 1: OAuth Authentication (Recommended)

# Create virtual environment

python3 -m venv venv1. **Run the setup wizard**



# Activate it```bash

source venv/bin/activate  # Linux/macOSpython -m ytmusicapi oauth

# OR```

venv\Scripts\activate     # Windows

```2. **Follow the prompts:**



3. **Install dependencies**   - Visit the URL provided

```bash   - Sign in to your Google account

pip install -e .   - Grant permissions

```   - Copy the code back to the terminal



---3. **Save the output**

   - The wizard will create `oauth.json` automatically

## 🔐 Authentication Setup   - Keep this file secure and never commit it to git



You **must** authenticate before using the server. Choose **one** method:#### Method 2: Browser Authentication



### Option A: Browser Cookie Authentication (Recommended for simplicity)1. **Open YouTube Music**



1. Open [music.youtube.com](https://music.youtube.com) and ensure you're **logged in**   - Go to [https://music.youtube.com](https://music.youtube.com)

2. Open Developer Tools (`F12` or `Ctrl+Shift+I`)   - Make sure you're logged in

3. Go to the **Network** tab

4. Refresh the page or click around on YouTube Music2. **Open Browser Developer Tools**

5. Find any POST request (filter by "POST" method)

6. Click on the request → **Headers** tab   - Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)

7. Copy the **entire request headers**   - Or right-click anywhere and select "Inspect"



8. Create `browser.json` using the setup helper:3. **Go to Network Tab**

```bash

python3 -c "   - Click the "Network" tab

from ytmusicapi import setup   - Make sure recording is enabled (red dot)

headers_raw = '''PASTE YOUR HEADERS HERE'''

setup(filepath='browser.json', headers_raw=headers_raw)4. **Filter by "browse"**

"

```   - In the filter box, type: `browse`



**Important**: The cookies expire after ~2 years or when you log out. If authentication fails, repeat these steps with fresh cookies.5. **Trigger a Request**



### Option B: OAuth Authentication (Recommended for long-term use)   - Click on "Library" or "Home" in YouTube Music

   - Or click on any playlist or song

OAuth requires setting up Google Cloud credentials. See [docs/OAUTH_SETUP.md](docs/OAUTH_SETUP.md) for detailed instructions.

6. **Copy Authentication Headers**

---

   - Find a POST request to `browse?...` in the Network tab

## 🎯 Usage   - Right-click → "Copy" → "Copy as cURL"

   - Paste into a text editor

### Testing with MCP Inspector

7. **Extract the Cookie**

Test the server interactively before integrating with Claude:

   - Find the `-H 'cookie: ...'` line

```bash   - Copy everything after `cookie: ` (very long string)

npx @modelcontextprotocol/inspector venv/bin/python server.py

```8. **Create browser.json**

   - Copy `browser.json.example` to `browser.json`

This opens a web interface at `http://localhost:6274` where you can:   - Replace `PASTE_YOUR_YOUTUBE_MUSIC_COOKIE_HERE` with your cookie

- View all available tools   - Save the file

- Test each tool with parameters

- See real-time responses### ⚠️ Security Warning

- Debug authentication issues

**NEVER commit `oauth.json` or `browser.json` to version control!** These files contain your authentication credentials. The `.gitignore` file is configured to exclude them, but always double-check.

---

### Testing the Server

## 🤖 Claude Desktop Integration

You can test the server using the MCP Inspector:

See the [**Claude Desktop Setup Guide**](docs/CLAUDE_SETUP.md) for complete instructions.

```bash

### Quick Setupnpx @modelcontextprotocol/inspector python server.py

```

1. Locate your Claude config file:

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`This will open a browser interface at `http://localhost:6789` where you can test all tools.

   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

   - **Linux**: `~/.config/Claude/claude_desktop_config.json`## 🤖 Connecting to Claude Desktop



2. Add the server configuration (use **absolute paths**):### macOS/Linux

```json

{1. **Edit Claude Desktop config**

  "mcpServers": {

    "youtube-music": {```bash

      "command": "/absolute/path/to/youtubemusic-mcp/venv/bin/python",# macOS

      "args": ["/absolute/path/to/youtubemusic-mcp/server.py"]code ~/Library/Application\ Support/Claude/claude_desktop_config.json

    }

  }# Linux

}code ~/.config/Claude/claude_desktop_config.json

``````



3. Restart Claude Desktop2. **Add the server configuration**



4. Start chatting! Try:```json

   - *"How many songs have I liked on YouTube Music?"*{

   - *"What are my top 5 artists?"*  "mcpServers": {

   - *"Search for songs by The Weeknd"*    "youtube-music": {

   - *"Create a playlist called 'Road Trip' with upbeat rock songs"*      "command": "python",

      "args": ["/absolute/path/to/youtube-music-mcp/server.py"]

---    }

  }

## 🛠 Available Tools}

```

### `get_liked_songs_count`

Get the total number of songs you've liked.**Important:** Replace `/absolute/path/to/youtube-music-mcp/` with the actual absolute path to your project folder.



**Parameters**: None### Windows



**Example prompt**: *"How many songs have I liked?"*1. **Edit Claude Desktop config**



---Located at: `%APPDATA%\Claude\claude_desktop_config.json`



### `get_library_stats````json

Get comprehensive statistics about your music library.{

  "mcpServers": {

**Parameters**: None    "youtube-music": {

      "command": "python",

**Returns**:      "args": ["C:\\absolute\\path\\to\\youtube-music-mcp\\server.py"]

```json    }

{  }

  "total_songs": 1234,}

  "total_playlists": 15,```

  "total_artists": 456,

  "total_albums": 789### Using a Virtual Environment

}

```If you're using a virtual environment (recommended), use the full path to the Python interpreter:



**Example prompt**: *"Show me my library statistics"*```json

{

---  "mcpServers": {

    "youtube-music": {

### `search_music`      "command": "/absolute/path/to/youtube-music-mcp/venv/bin/python",

Search for music content on YouTube Music.      "args": ["/absolute/path/to/youtube-music-mcp/server.py"]

    }

**Parameters**:  }

- `query` (string, **required**): Search term}

- `filter` (string, optional): Content type - `"songs"`, `"videos"`, `"albums"`, `"artists"`, `"playlists"````

- `limit` (number, optional): Max results (default: 20)

### Verify Connection

**Example prompts**:

- *"Search for Bohemian Rhapsody"*1. **Restart Claude Desktop completely** (Quit and reopen)

- *"Find albums by Taylor Swift"*2. Look for the 🔌 icon in Claude's interface

- *"Search for jazz playlists"*3. You should see "youtube-music" listed as a connected server

4. Start asking questions!

---

## 💬 Example Usage with Claude

### `get_top_artists`

Get your most played artists based on listening history.Once connected, you can ask Claude natural language questions:



**Parameters**:```

- `limit` (number, optional): Max artists (default: 10, max: 50)"How many songs do I have in my library?"

"Who are my top 10 artists?"

**Example prompt**: *"Who are my top 10 artists?"*"Search for Radiohead albums"

"Find me songs similar to Bohemian Rhapsody"

---"Give me 20 recommendations based on my taste"

"Create a playlist called 'Road Trip Mix' with 15 upbeat rock songs"

### `find_similar_songs````

Discover songs similar to a given track.

Claude will automatically use the appropriate tools to answer your questions!

**Parameters**:

- `song_query` (string, **required**): Song name or "Artist - Song" format## 🛠️ Development

- `limit` (number, optional): Max results (default: 20)

### Project Structure

**Example prompts**:

- *"Find songs similar to Blinding Lights"*```

- *"Songs like The Weeknd - Starboy"*youtube-music-mcp/

├── server.py                 # Main MCP server (~600 lines)

---├── pyproject.toml           # Python project configuration

├── oauth.json               # OAuth credentials (git-ignored, you create this)

### `get_recommendations`├── oauth.json.example       # OAuth template

Get personalized music recommendations based on a seed song.├── browser.json             # Browser auth (git-ignored, you create this)

├── browser.json.example     # Browser auth template

**Parameters**:├── .gitignore              # Excludes secrets and build files

- `seed_song` (string, **required**): Song to base recommendations on└── README.md               # This file

- `limit` (number, optional): Max results (default: 20)```



**Example prompt**: *"Recommend songs based on Levitating by Dua Lipa"*### Tech Stack



---- **Runtime:** Python 3.10+

- **MCP SDK:** `mcp` for Model Context Protocol

### `create_playlist_from_songs`- **YouTube Music API:** `ytmusicapi` - Official unofficial API

Create a new YouTube Music playlist from song queries.- **Async:** Native Python asyncio



**Parameters**:### Running Tests

- `playlist_name` (string, **required**): Name for the new playlist

- `song_queries` (array, **required**): List of song search queries```bash

- `description` (string, optional): Playlist descriptionpytest

```

**Example prompt**: 

*"Create a playlist called 'Workout Mix' with these songs: 'Eye of the Tiger', 'Stronger by Kanye West', 'Lose Yourself'"*### Code Formatting



---```bash

black server.py

## 🐛 Troubleshootingruff check server.py

```

### Authentication Errors

## 🐛 Troubleshooting

**Problem**: *"Sign in to listen to your liked tracks"* or similar errors

### "No authentication file found"

**Solution**:

1. Your cookies have expired - get **fresh cookies** from your browser (see [Authentication Setup](#-authentication-setup))**Problem:** Server can't find `oauth.json` or `browser.json`.

2. Ensure you're **logged in** to music.youtube.com when copying headers

3. Make sure `browser.json` has the correct `authorization` header with SAPISIDHASH**Solution:**



### Connection Issues1. Make sure you've created either `oauth.json` or `browser.json` in the project root

2. Check that the file is named exactly as shown (not `.txt` or other extension)

**Problem**: Claude Desktop doesn't detect the server3. Verify the file is in the same directory as `server.py`



**Solution**:### "Failed to initialize YouTube Music"

1. Verify you're using **absolute paths** in `claude_desktop_config.json`

2. Confirm the Python path points to your **venv** Python: `which python` (in activated venv)**Problem:** Authentication credentials are invalid or expired.

3. Check Claude Desktop logs:

   - **macOS**: `~/Library/Logs/Claude/`**Solution:**

   - **Windows**: `%APPDATA%\Claude\logs\`

**For OAuth:**

### Import/Dependency Errors

1. Delete `oauth.json`

**Problem**: `ModuleNotFoundError` or import errors2. Run `python -m ytmusicapi oauth` again

3. Follow the setup process

**Solution**:

```bash**For Browser Auth:**

# Ensure you're in the project directory

cd youtubemusic-mcp1. Your cookie may have expired - extract a fresh one

2. Make sure you're logged into YouTube Music in the same browser

# Activate virtual environment3. Try using a different browser's cookie

source venv/bin/activate  # or venv\Scripts\activate on Windows

### Server Not Showing in Claude Desktop

# Reinstall dependencies

pip install -e .**Problem:** Claude doesn't show the youtube-music server.

```

**Solution:**

### Server Won't Start

1. **Check the config file path:**

**Problem**: Server crashes or exits immediately

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Solution**:   - Linux: `~/.config/Claude/claude_desktop_config.json`

1. Check that `browser.json` or `oauth.json` exists   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Test authentication manually:

   ```bash2. **Verify the path is absolute:**

   python3 -c "from ytmusicapi import YTMusic; yt = YTMusic('browser.json'); print('✅ Auth works!')"

   ```   - Use full path like `/Users/yourname/projects/youtube-music-mcp/server.py`

3. Run server directly to see errors:   - Don't use `~` or relative paths

   ```bash   - On Windows, use backslashes: `C:\\Users\\...`

   python server.py

   ```3. **Check Python is in PATH:**



---   ```bash

   which python  # macOS/Linux

## 📁 Project Structure   where python  # Windows

   ```

```

youtubemusic-mcp/4. **Restart Claude Desktop completely:**

├── server.py                   # Main MCP server implementation

├── pyproject.toml              # Python project configuration & dependencies   - Quit Claude (not just close the window)

├── README.md                   # This file   - Wait a few seconds

├── LICENSE                     # MIT license   - Reopen Claude

├── .gitignore                  # Git ignore rules (excludes auth files)

│5. **Check Claude's logs for errors:**

├── docs/                       # Documentation   - macOS: `~/Library/Logs/Claude/`

│   ├── CLAUDE_SETUP.md         # Claude Desktop integration guide   - Look for error messages related to MCP servers

│   ├── OAUTH_SETUP.md          # OAuth authentication guide

│   └── CONTRIBUTING.md         # Contribution guidelines### "Empty library results"

│

├── examples/                   # Example files**Problem:** Library methods return no results even though you have songs.

│   ├── oauth.json.example      # OAuth configuration template

│   └── browser.json.example    # Browser auth template**Solution:**

│

└── venv/                       # Virtual environment (not in git)1. Make sure you're logged into the correct YouTube Music account

```2. Try switching to OAuth authentication if using browser auth

3. Check that your YouTube Music library actually has content (not YouTube premium library)

---4. Some users have multiple YouTube accounts - make sure you're authenticated with the right one



## 🤝 Contributing### Python Package Import Errors



Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.**Problem:** `ImportError` or `ModuleNotFoundError`.



### Quick Contribution Guide**Solution:**



1. Fork the repository1. Make sure you've installed dependencies: `pip install -e .`

2. Create a feature branch: `git checkout -b feature/amazing-feature`2. If using a virtual environment, make sure it's activated

3. Make your changes3. Check Python version: `python --version` (must be 3.10+)

4. Test thoroughly4. Try reinstalling: `pip install --force-reinstall ytmusicapi mcp`

5. Commit: `git commit -m 'Add amazing feature'`

6. Push: `git push origin feature/amazing-feature`## 📝 API Features & Limitations

7. Open a Pull Request

### Supported Features

---

- ✅ **Full library access** - Get all your liked songs, artists, albums, playlists

## 📜 License- ✅ **Search** - Search for any music content on YouTube Music

- ✅ **Playlist creation** - Create and populate playlists programmatically

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.- ✅ **Playlist management** - Add/remove songs, edit metadata

- ✅ **Recommendations** - Get personalized suggestions

---- ✅ **Artist information** - Detailed artist data and discography

- ✅ **No rate limits** - Reasonable usage is unrestricted

## 🙏 Acknowledgments

### Current Limitations

- **[ytmusicapi](https://github.com/sigma67/ytmusicapi)** by sigma67 - Unofficial YouTube Music API

- **[Model Context Protocol](https://modelcontextprotocol.io/)** by Anthropic - MCP SDK- **No audio playback** - This is an API wrapper, not a player

- **Claude Desktop** by Anthropic - AI assistant integration- **No downloads** - Cannot download music files

- **No upload** - Cannot upload your own music (use YouTube Music app)

---- **Cookie expiration** - Browser auth cookies expire (use OAuth instead)



## 📞 Support## 🔒 Security Best Practices



- **Issues**: [GitHub Issues](https://github.com/codeRisshi25/youtubemusic-mcp/issues)1. **Never commit `oauth.json` or `browser.json`** - They contain your authentication credentials

- **Discussions**: [GitHub Discussions](https://github.com/codeRisshi25/youtubemusic-mcp/discussions)2. **Don't share your tokens** - They provide full access to your YouTube Music account

3. **Use OAuth when possible** - More secure than browser authentication

---4. **Rotate credentials periodically** - Especially for browser authentication

5. **Keep dependencies updated** - Run `pip install --upgrade ytmusicapi mcp`

<div align="center">

## 🤝 Contributing

**Built with ❤️ for the YouTube Music community**

Contributions are welcome! Please:

⭐ Star this repo if you find it useful!

1. Fork the repository

</div>2. Create a feature branch

3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [ytmusicapi](https://github.com/sigma67/ytmusicapi) for YouTube Music integration
- Inspired by the MCP community

## 📞 Support

Having issues? Please:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing GitHub issues
3. Create a new issue with:
   - Your Python version (`python --version`)
   - Operating system
   - Error messages (remove any sensitive info)
   - Steps to reproduce

## 🎯 Roadmap

Future features under consideration:

- [ ] Lyrics fetching
- [ ] Advanced playlist management (reorder, dedupe)
- [ ] Listen history tracking
- [ ] Genre-based recommendations
- [ ] Collaborative playlists
- [ ] Export/import playlists
- [ ] Integration with last.fm for scrobbling

---

**Built with ❤️ for music lovers and AI enthusiasts**

## ✨ Features

This MCP server provides 7 powerful tools:

1. **`get_liked_songs_count`** - Get total count of songs in your library (bypasses YouTube's 5000 display limit)
2. **`get_library_stats`** - Comprehensive library statistics with unique artists and averages
3. **`search_music`** - Search for songs, albums, artists, playlists, and videos
4. **`get_top_artists`** - Ranked list of your top artists with counts and percentages
5. **`find_similar_songs`** - Discover songs similar to any track
6. **`get_recommendations`** - Personalized recommendations based on your library
7. **`create_playlist_from_songs`** - Find songs for playlist creation (reports found songs)

## 🚀 Quick Start

### Prerequisites

- Node.js 18 or higher
- A YouTube Music account with songs in your library
- Access to browser developer tools (to extract authentication cookie)

### Installation

1. **Clone or download this repository**

```bash
git clone <your-repo-url>
cd youtube-music-mcp
```

2. **Install dependencies**

```bash
npm install
```

3. **Set up authentication** (see detailed instructions below)

Create a `headers.json` file with your YouTube Music cookie:

```json
{
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept": "*/*",
  "Accept-Language": "en-US,en;q=0.9",
  "Content-Type": "application/json",
  "X-Goog-AuthUser": "0",
  "x-origin": "https://music.youtube.com",
  "Cookie": "YOUR_COOKIE_HERE"
}
```

4. **Test the server**

```bash
npm run inspect
```

This opens the MCP Inspector at `http://localhost:6789` where you can test all tools.

## 🔐 Authentication Setup (Extract YouTube Music Cookie)

The server needs your YouTube Music authentication cookie to access your library. Here's how to get it:

### Step-by-Step Instructions

1. **Open YouTube Music**

   - Go to [https://music.youtube.com](https://music.youtube.com)
   - Make sure you're logged in to your account

2. **Open Browser Developer Tools**

   - Press `F12` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - Or right-click anywhere and select "Inspect"

3. **Go to Network Tab**

   - Click the "Network" tab in developer tools
   - Make sure recording is enabled (red dot should be visible)

4. **Filter by "browse"**

   - In the filter box, type: `browse`

5. **Trigger a Request**

   - Click on "Library" or "Home" in YouTube Music
   - Or click on any playlist or song

6. **Find the POST Request**

   - Look for a POST request to `browse?...` in the Network tab
   - Click on it to select it

7. **Copy the Cookie**

   - **Method A (Recommended):**

     - Right-click on the request → "Copy" → "Copy as cURL"
     - Paste into a text editor
     - Find the `-H 'cookie: ...'` line
     - Copy everything after `cookie: ` (it's a very long string)

   - **Method B:**
     - In the request details, go to "Headers" tab
     - Scroll down to "Request Headers"
     - Find "cookie:" header
     - Copy the entire value (very long string)

8. **Create headers.json**
   - Copy `headers.json.example` to `headers.json`
   - Replace `PASTE_YOUR_YOUTUBE_MUSIC_COOKIE_HERE` with your cookie
   - Save the file

### ⚠️ Security Warning

**NEVER commit `headers.json` to version control!** This file contains your authentication credentials. The `.gitignore` file is configured to exclude it, but always double-check before committing.

## 🧪 Testing with MCP Inspector

The MCP Inspector is a browser-based tool for testing your server:

```bash
npm run inspect
```

This will:

1. Start the server
2. Open your browser at `http://localhost:6789`
3. Show all available tools
4. Let you test each tool with custom inputs

### Example Tests

Try these in the inspector:

- **Get song count:** Use `get_liked_songs_count` (no parameters)
- **Search for music:** Use `search_music` with `{ "query": "Pink Floyd" }`
- **Get top artists:** Use `get_top_artists` with `{ "limit": 5 }`
- **Get recommendations:** Use `get_recommendations` with `{ "count": 10 }`

## 🤖 Connecting to Claude Desktop

### macOS/Linux

1. **Build the server**

```bash
npm run build
```

2. **Edit Claude Desktop config**

```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
code ~/.config/Claude/claude_desktop_config.json
```

3. **Add the server configuration**

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "node",
      "args": ["/absolute/path/to/youtube-music-mcp/dist/index.js"]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/youtube-music-mcp/` with the actual absolute path to your project folder.

### Windows

1. **Build the server**

```bash
npm run build
```

2. **Edit Claude Desktop config**

Located at: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "node",
      "args": ["C:\\absolute\\path\\to\\youtube-music-mcp\\dist\\index.js"]
    }
  }
}
```

### Verify Connection

1. **Restart Claude Desktop completely** (Quit and reopen)
2. Look for the 🔌 icon in Claude's interface
3. You should see "youtube-music" listed as a connected server
4. Start asking questions!

## 💬 Example Usage with Claude

Once connected, you can ask Claude natural language questions:

```
"How many songs do I have in my library?"
"Who are my top 10 artists?"
"Search for Radiohead albums"
"Find me songs similar to Bohemian Rhapsody"
"Give me 20 recommendations based on my taste"
"Create a playlist called 'Road Trip Mix' with 15 upbeat rock songs"
```

Claude will automatically use the appropriate tools to answer your questions!

## 🛠️ Development

### Available Scripts

- `npm run dev` - Run server in development mode with auto-reload
- `npm run build` - Build TypeScript to JavaScript
- `npm start` - Run built server
- `npm run inspect` - Open MCP Inspector for testing

### Project Structure

```
youtube-music-mcp/
├── src/
│   └── index.ts          # Main server implementation (~600 lines)
├── dist/                 # Built JavaScript (generated)
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── headers.json          # Your auth cookie (git-ignored, you create this)
├── headers.json.example  # Template for headers.json
├── .env.example          # Environment template
├── .gitignore           # Excludes secrets and build files
└── README.md            # This file
```

### Tech Stack

- **Runtime:** Node.js 18+ with ES modules
- **Language:** TypeScript (strict mode)
- **MCP SDK:** `@modelcontextprotocol/sdk` v1.0.4+
- **YouTube Music API:** `ytmusic-api` v5.3.1+ (actively maintained)
- **Validation:** Zod for schema validation
- **Dev Tools:** tsx for development, TypeScript compiler for builds

## 🐛 Troubleshooting

### "headers.json not found"

**Problem:** Server can't find your authentication file.

**Solution:**

1. Make sure `headers.json` exists in the project root (same directory as `package.json`)
2. Check that you copied `headers.json.example` and filled in your cookie
3. Verify the file is named exactly `headers.json` (not `.txt` or other extension)

### "Cookie not found in headers.json"

**Problem:** The Cookie field is missing or empty.

**Solution:**

1. Open `headers.json` in a text editor
2. Make sure the `Cookie` field has your actual YouTube Music cookie
3. The cookie should be a very long string (hundreds of characters)
4. Don't use the placeholder text from the example file

### Authentication Errors

**Problem:** "Failed to initialize YouTube Music" or API errors.

**Solution:**

1. Your cookie may have expired - extract a fresh one
2. Make sure you're logged into YouTube Music in the same browser
3. Try using a different browser's cookie
4. Clear your browser cache and get a new cookie

### Server Not Showing in Claude Desktop

**Problem:** Claude doesn't show the youtube-music server.

**Solution:**

1. **Check the config file path:**

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Verify the path is absolute:**

   - Use full path like `/Users/yourname/projects/youtube-music-mcp/dist/index.js`
   - Don't use `~` or relative paths
   - On Windows, use backslashes: `C:\\Users\\...`

3. **Make sure the server is built:**

   ```bash
   npm run build
   ```

4. **Restart Claude Desktop completely:**

   - Quit Claude (not just close the window)
   - Wait a few seconds
   - Reopen Claude

5. **Check Claude's logs for errors:**
   - macOS: `~/Library/Logs/Claude/`
   - Look for error messages related to MCP servers

### "No results found" When Searching

**Problem:** Searches return no results even for popular songs.

**Solution:**

1. Your cookie might be expired - get a fresh one
2. Try more specific search terms
3. Check that YouTube Music is accessible in your region
4. Verify your internet connection

### TypeScript Build Errors

**Problem:** `npm run build` fails with type errors.

**Solution:**

1. Make sure you're using Node.js 18 or higher: `node --version`
2. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
3. Make sure all dependencies are installed: `npm install`
4. Check that TypeScript version is compatible: `npx tsc --version`

## 📝 API Limitations

- **Playlist Creation:** The `create_playlist_from_songs` tool finds songs but doesn't actually create playlists due to YouTube Music API limitations. It provides a detailed report of found songs that you can manually add to a playlist.

- **Genre Detection:** Not currently implemented as it requires external APIs. Future feature.

- **OAuth Authentication:** Currently uses cookie-based authentication. OAuth support may be added in future versions.

## 🔒 Security Best Practices

1. **Never commit `headers.json`** - It contains your authentication credentials
2. **Don't share your cookie** - It provides full access to your YouTube Music account
3. **Rotate cookies periodically** - Extract a fresh cookie every few weeks
4. **Use environment-specific configs** - Don't hardcode paths or credentials
5. **Keep dependencies updated** - Run `npm audit` regularly

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `npm run inspect`
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [ytmusic-api](https://github.com/nickp10/ytmusic-api) for YouTube Music integration
- Inspired by the MCP community

## 📞 Support

Having issues? Please:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Search existing GitHub issues
3. Create a new issue with:
   - Your Node.js version
   - Operating system
   - Error messages (remove any sensitive info)
   - Steps to reproduce

---

**Built with ❤️ for music lovers and AI enthusiasts**
