# Claude Desktop Setup Guide

This guide provides detailed instructions for integrating the YouTube Music MCP server with Claude Desktop.

## Prerequisites

Before you begin:

- ✅ Completed [Installation](../README.md#-installation)
- ✅ Completed [Authentication Setup](../README.md#-authentication-setup)
- ✅ Tested the server with MCP Inspector
- ✅ Claude Desktop installed on your system

---

## Step 1: Locate Your Configuration File

Claude Desktop stores its MCP server configuration in a JSON file. The location varies by operating system:

### macOS
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

### Linux
```bash
~/.config/Claude/claude_desktop_config.json
```

**Note**: If the file doesn't exist, create it manually.

---

## Step 2: Get Absolute Paths

You need **absolute paths** (not relative paths) for the configuration. Here's how to get them:

### Get the Python Executable Path

With your virtual environment **activated**:

```bash
# macOS/Linux
which python

# Windows (PowerShell)
(Get-Command python).Path

# Windows (CMD)
where python
```

**Example output**:
```
/home/risshi/data/youtubemusic-mcp/venv/bin/python
```

### Get the Server Script Path

```bash
# macOS/Linux - from project directory
pwd
# Output: /home/risshi/data/youtubemusic-mcp

# Then append: /server.py

# Windows (PowerShell)
Get-Location
# Then append: \server.py
```

**Full path example**:
```
/home/risshi/data/youtubemusic-mcp/server.py
```

---

## Step 3: Edit Configuration File

Open the configuration file in your preferred text editor:

```bash
# macOS
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
code ~/.config/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

---

## Step 4: Add Server Configuration

### If the file is empty or new:

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

### If you already have other MCP servers:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "node",
      "args": ["/path/to/existing/server.js"]
    },
    "youtube-music": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

### Platform-Specific Examples

#### macOS Example
```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "/Users/risshi/projects/youtubemusic-mcp/venv/bin/python",
      "args": ["/Users/risshi/projects/youtubemusic-mcp/server.py"]
    }
  }
}
```

#### Linux Example
```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "/home/risshi/data/youtubemusic-mcp/venv/bin/python",
      "args": ["/home/risshi/data/youtubemusic-mcp/server.py"]
    }
  }
}
```

#### Windows Example
```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "C:\\Users\\Risshi\\Projects\\youtubemusic-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\Risshi\\Projects\\youtubemusic-mcp\\server.py"]
    }
  }
}
```

**Important**: 
- On Windows, use **double backslashes** (`\\`) in paths
- On macOS/Linux, use **forward slashes** (`/`)
- **Always use absolute paths** - never use `~` or relative paths

---

## Step 5: Save and Restart Claude Desktop

1. **Save** the configuration file
2. **Quit Claude Desktop completely**:
   - macOS: `Cmd+Q` or Claude → Quit Claude
   - Windows: Right-click taskbar icon → Quit
   - Linux: File → Quit
3. **Wait 5 seconds**
4. **Reopen Claude Desktop**

---

## Step 6: Verify Connection

### Check for the Server

1. Open Claude Desktop
2. Look for the **🔌 (plug) icon** in the bottom-right or status area
3. Click it to see connected MCP servers
4. You should see **"youtube-music"** listed

### Test with a Query

Try asking Claude:

```
"How many songs do I have liked on YouTube Music?"
```

If everything is working, Claude will:
1. Recognize it needs YouTube Music data
2. Use the `get_liked_songs_count` tool
3. Return your actual song count

---

## Troubleshooting

### Server Not Appearing

**Problem**: The youtube-music server doesn't show up in Claude's MCP server list

**Solutions**:

1. **Check JSON syntax**:
   - Use a JSON validator: https://jsonlint.com/
   - Ensure all braces, brackets, and quotes match
   - No trailing commas

2. **Verify absolute paths**:
   ```bash
   # Test that the Python path exists
   ls -l /absolute/path/to/venv/bin/python
   
   # Test that the server script exists
   ls -l /absolute/path/to/server.py
   ```

3. **Check file permissions**:
   ```bash
   # macOS/Linux - make server.py executable
   chmod +x /absolute/path/to/server.py
   ```

4. **Check Claude logs**:
   - **macOS**: `~/Library/Logs/Claude/`
   - **Windows**: `%APPDATA%\Claude\logs\`
   - Look for error messages related to MCP servers

---

### Connection Errors

**Problem**: Server appears but Claude can't communicate with it

**Solutions**:

1. **Test the server manually**:
   ```bash
   cd /path/to/youtubemusic-mcp
   source venv/bin/activate
   python server.py
   ```
   
   - Server should start without errors
   - Press `Ctrl+C` to stop

2. **Check authentication**:
   ```bash
   python3 -c "from ytmusicapi import YTMusic; yt = YTMusic('browser.json'); print('✅ Auth works!')"
   ```

3. **Reinstall dependencies**:
   ```bash
   source venv/bin/activate
   pip install --force-reinstall mcp ytmusicapi
   ```

---

### Authentication Fails in Claude

**Problem**: Server connects but returns authentication errors

**Solution**:

Your `browser.json` or `oauth.json` cookies may have expired. Get fresh authentication credentials:

1. **For browser auth**: Follow [Browser Cookie Authentication](../README.md#option-a-browser-cookie-authentication-recommended-for-simplicity)
2. **For OAuth**: Follow [OAuth Setup](OAUTH_SETUP.md)

---

### Tools Not Working

**Problem**: Server connects but tools fail or return errors

**Solutions**:

1. **Test with MCP Inspector first**:
   ```bash
   npx @modelcontextprotocol/inspector venv/bin/python server.py
   ```
   - If tools work here but not in Claude, it's a Claude configuration issue
   - If tools don't work here, it's a server/auth issue

2. **Check Python version**:
   ```bash
   python --version
   # Must be 3.10 or higher
   ```

3. **Update dependencies**:
   ```bash
   pip install --upgrade mcp ytmusicapi
   ```

---

## Advanced Configuration

### Environment Variables

If you need to pass environment variables to the server:

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "YTMUSIC_AUTH_FILE": "/custom/path/to/browser.json"
      }
    }
  }
}
```

### Using System Python (Not Recommended)

If you're not using a virtual environment (not recommended):

```json
{
  "mcpServers": {
    "youtube-music": {
      "command": "python3",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

**Warning**: This requires `mcp` and `ytmusicapi` to be installed globally.

---

## Usage Examples

Once integrated, you can ask Claude:

### Library Queries
- *"How many songs have I liked on YouTube Music?"*
- *"What are my library statistics?"*
- *"Show me my top 10 artists"*

### Search & Discovery
- *"Search for songs by Pink Floyd"*
- *"Find me jazz playlists"*
- *"What are some songs similar to Hotel California?"*

### Recommendations
- *"Give me 20 music recommendations based on Blinding Lights"*
- *"Recommend similar artists to The Weeknd"*

### Playlist Management
- *"Create a playlist called 'Chill Vibes' with lo-fi hip hop songs"*
- *"Make a workout playlist with high-energy rock songs"*

---

## Next Steps

- Explore all [Available Tools](../README.md#-available-tools)
- Read the [Contributing Guide](CONTRIBUTING.md)
- Check out [OAuth Setup](OAUTH_SETUP.md) for long-term authentication

---

## Getting Help

If you're still having issues:

1. Check the [main README troubleshooting section](../README.md#-troubleshooting)
2. Search [existing GitHub issues](https://github.com/codeRisshi25/youtubemusic-mcp/issues)
3. Create a new issue with:
   - Your OS and Python version
   - Claude Desktop version
   - Complete error messages from logs
   - Your `claude_desktop_config.json` (remove any sensitive paths)

---

**Happy music discovery with Claude! 🎵**
