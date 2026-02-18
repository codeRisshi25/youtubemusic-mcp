# Authentication Update Guide

When you see authentication errors (usually after 6–24 months), update your cookies:

## Quick Update (2 steps)

1. **Get fresh cookies:**
   - Go to [music.youtube.com](https://music.youtube.com) (make sure you're logged in)
   - Press F12 → Network tab → Refresh page
   - Click any request → Headers → Copy the entire `cookie:` value

2. **Save to file:**
   - Paste into `cookie.txt` in the project folder (overwrite the old contents)
   - Restart the MCP server — it auto-generates `browser.json` on startup

That's it! No scripts required.

### Optional: validate before restarting

```bash
python update_auth.py
```

The script will write `browser.json`, test the connection, and report success/failure.

> **How it works:** The server (and `update_auth.py`) only stores Cookie + origin
> headers. `ytmusicapi` regenerates the SAPISIDHASH internally on every request,
> so no manual hash generation is needed.

## Alternative: OAuth (Auto-refreshing)

For long-term use without manual updates:

```bash
python -m ytmusicapi oauth
```

See `docs/OAUTH_SETUP.md` for detailed OAuth setup.

## Troubleshooting

**"does not look like a valid YouTube cookie string"**: Make sure you copied the complete `cookie:` header value, not just part of it. It must contain `SAPISID=…` and `SID=…`.

**"Auth works but playlist creation fails"**: Paste fresh cookies into `cookie.txt` and restart.

**Script not found**: Make sure you're in the project directory and venv is activated.
