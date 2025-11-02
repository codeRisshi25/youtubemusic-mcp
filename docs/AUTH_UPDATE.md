# Authentication Update Guide

When you see authentication errors (usually after 6 months), update your cookies:

## Quick Update (3 steps)

1. **Get fresh cookies:**

   - Go to [music.youtube.com](https://music.youtube.com) (make sure you're logged in)
   - Press F12 → Network tab → Refresh page
   - Click any request → Request Headers → Copy the entire `cookie:` value

2. **Save to file:**

   - Create/open `cookie.txt` in the project folder
   - Paste the cookie string
   - Save and close

3. **Run updater:**
   ```bash
   python update_auth.py
   ```

That's it! The script will:

- Extract SAPISID from your cookies
- Generate fresh authorization hash
- Update `browser.json`
- Test authentication
- Delete `cookie.txt` for security

## Alternative: OAuth (Auto-refreshing)

For long-term use without manual updates:

```bash
python -m ytmusicapi oauth
```

See `docs/OAUTH_SETUP.md` for detailed OAuth setup.

## Troubleshooting

**"SAPISID not found"**: Make sure you copied the complete cookie string, not just part of it

**"Auth works but playlist creation fails"**: Run `update_auth.py` again with fresh cookies

**Script not found**: Make sure you're in the project directory and venv is activated
