# OAuth Authentication Setup Guide

This guide explains how to set up OAuth authentication for the YouTube Music MCP server. OAuth is recommended for long-term use as tokens automatically refresh.

---

## Overview

**Browser authentication** (cookies) expires after ~2 years or when you log out. **OAuth** provides:

- ✅ **Auto-refreshing tokens** - no need to manually update credentials
- ✅ **More secure** - tokens can be revoked without password change
- ✅ **Better for production** - suitable for long-term deployments

**Downside**: More complex initial setup requiring Google Cloud Console access.

---

## Prerequisites

- A Google account
- Access to [Google Cloud Console](https://console.cloud.google.com/)
- YouTube Music account linked to your Google account

---

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** at the top
3. Click **"NEW PROJECT"**
4. Enter project name: `YouTube Music MCP`
5. Click **"CREATE"**
6. Wait for project creation (usually < 30 seconds)
7. Select your new project from the project dropdown

---

## Step 2: Enable YouTube Data API

1. In the left sidebar, go to **"APIs & Services"** → **"Library"**
2. Search for: `YouTube Data API v3`
3. Click on **"YouTube Data API v3"**
4. Click **"ENABLE"**
5. Wait for activation

---

## Step 3: Create OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"CREATE"**

### Configure OAuth Consent Screen

**App information**:
- **App name**: `YouTube Music MCP Server`
- **User support email**: Your email
- **App logo**: (optional)

**App domain** (optional):
- Leave blank for personal use

**Developer contact information**:
- **Email addresses**: Your email

Click **"SAVE AND CONTINUE"**

### Scopes

1. Click **"ADD OR REMOVE SCOPES"**
2. Search for: `youtube`
3. Select:
   - ✅ `YouTube Data API v3` → `.../auth/youtube`
   - ✅ `YouTube Data API v3` → `.../auth/youtube.readonly`
4. Click **"UPDATE"**
5. Click **"SAVE AND CONTINUE"**

### Test Users

1. Click **"ADD USERS"**
2. Enter your Google account email
3. Click **"ADD"**
4. Click **"SAVE AND CONTINUE"**

### Summary

Review and click **"BACK TO DASHBOARD"**

---

## Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

### Configure OAuth Client

1. **Application type**: Select **"Desktop app"**
2. **Name**: `YouTube Music MCP Client`
3. Click **"CREATE"**

### Download Credentials

1. A popup appears with your client ID and secret
2. Click **"DOWNLOAD JSON"**
3. Save the file as `client_secret.json`
4. Click **"OK"**

---

## Step 5: Set Up ytmusicapi OAuth

### Move client_secret.json

```bash
# Move the downloaded file to your project directory
mv ~/Downloads/client_secret_*.json /path/to/youtubemusic-mcp/client_secret.json
```

### Run OAuth Setup

```bash
cd /path/to/youtubemusic-mcp
source venv/bin/activate  # Activate virtual environment

python3 -m ytmusicapi oauth
```

### Complete Authorization Flow

1. The command will display a URL
2. **Copy the URL** and open it in your browser
3. **Sign in** with your Google account (the one added as a test user)
4. You'll see: *"Google hasn't verified this app"*
   - Click **"Advanced"**
   - Click **"Go to YouTube Music MCP Server (unsafe)"**
5. Review permissions and click **"Allow"**
6. You'll see: *"The authentication flow has completed"*
7. Copy the **authorization code** from the page
8. **Paste the code** back into the terminal
9. Press **Enter**

### Verify oauth.json Created

```bash
ls -l oauth.json
# Should show the file with recent timestamp
```

---

## Step 6: Test Authentication

```bash
python3 -c "
from ytmusicapi import YTMusic
yt = YTMusic('oauth.json')
print('✅ OAuth authentication successful!')
print(f'Liked songs: {len(yt.get_liked_songs(limit=1))} (showing 1)')
"
```

Expected output:
```
✅ OAuth authentication successful!
Liked songs: 1 (showing 1)
```

---

## Step 7: Update Server Configuration

The server automatically detects `oauth.json` if `browser.json` doesn't exist. No code changes needed!

### Test the Server

```bash
npx @modelcontextprotocol/inspector venv/bin/python server.py
```

The server will now use OAuth authentication.

---

## Security Best Practices

### Protect Your Credentials

1. **Never commit `oauth.json`** - it's already in `.gitignore`
2. **Never commit `client_secret.json`** - add it to `.gitignore`:
   ```bash
   echo "client_secret.json" >> .gitignore
   ```
3. **Keep tokens secure** - don't share or expose them

### Token Refresh

OAuth tokens automatically refresh! The `ytmusicapi` library handles this:

- **Access token** expires in ~1 hour
- **Refresh token** is used to get new access tokens
- **Refresh happens automatically** when making API calls

### Revoke Access

If compromised, revoke access:

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find **"YouTube Music MCP Server"**
3. Click **"Remove Access"**
4. Delete `oauth.json` from your project
5. Run `python3 -m ytmusicapi oauth` again to re-authorize

---

## Troubleshooting

### "The OAuth client was not found"

**Problem**: Invalid client ID or secret

**Solution**:
1. Re-download `client_secret.json` from Google Cloud Console
2. Make sure it's named exactly `client_secret.json`
3. Run `python3 -m ytmusicapi oauth` again

---

### "Access blocked: YouTube Music MCP Server has not completed Google verification"

**Problem**: App not verified by Google

**Solution**:
This is expected for personal projects. To bypass:
1. When seeing the warning, click **"Advanced"**
2. Click **"Go to YouTube Music MCP Server (unsafe)"**
3. This is safe because it's your own app

**Alternative**: Publish the app (complex, not needed for personal use)

---

### "Unauthorized: invalid_grant"

**Problem**: Refresh token expired or revoked

**Solution**:
1. Delete `oauth.json`
2. Run `python3 -m ytmusicapi oauth` again
3. Complete the authorization flow

---

### "This app is blocked"

**Problem**: You didn't add yourself as a test user

**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **OAuth consent screen**
3. Scroll to **"Test users"**
4. Click **"ADD USERS"**
5. Add your Google account email
6. Try authorization again

---

### Token File Not Found

**Problem**: `oauth.json` not created after authorization

**Solution**:
1. Make sure you ran `python3 -m ytmusicapi oauth` (not `ytmusicapi oauth`)
2. Check you're in the project directory
3. Verify you pasted the authorization code correctly
4. Try the process again

---

## OAuth vs Browser Authentication Comparison

| Feature | OAuth | Browser Cookies |
|---------|-------|-----------------|
| **Setup complexity** | High (Google Cloud) | Low (just copy cookies) |
| **Token lifespan** | Auto-refreshing | ~2 years |
| **Security** | More secure | Less secure |
| **Maintenance** | None (auto-refresh) | Manual refresh every ~2 years |
| **Recommended for** | Production, long-term | Quick testing, personal use |

---

## Next Steps

- Test the server with [MCP Inspector](../README.md#testing-with-mcp-inspector)
- Set up [Claude Desktop integration](CLAUDE_SETUP.md)
- Start using the [available tools](../README.md#-available-tools)

---

## Need Help?

- Check the [main README troubleshooting](../README.md#-troubleshooting)
- Search [GitHub issues](https://github.com/codeRisshi25/youtubemusic-mcp/issues)
- Create a new issue with your OAuth setup step where you got stuck

---

**Enjoy secure, long-term YouTube Music access! 🎵**
