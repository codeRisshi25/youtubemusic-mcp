#!/usr/bin/env python3
"""
Simple cookie updater for YouTube Music MCP Server.
Just paste your raw cookie string and this handles the rest.
"""

import json
import hashlib
import time
from pathlib import Path


def generate_sapisidhash(sapisid: str) -> str:
    """Generate SAPISIDHASH for YouTube Music authentication."""
    timestamp = int(time.time())
    hash_string = f"{timestamp} {sapisid} https://music.youtube.com"
    hash_value = hashlib.sha1(hash_string.encode()).hexdigest()
    return f"SAPISIDHASH {timestamp}_{hash_value}"


def extract_sapisid(cookie_string: str) -> str:
    """Extract SAPISID value from cookie string."""
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if cookie.startswith('SAPISID='):
            return cookie.split('=', 1)[1]
    raise ValueError("SAPISID not found in cookies")


def update_auth():
    """Update browser.json with fresh cookies."""
    cookie_file = Path("cookie.txt")
    
    # Check if cookie.txt exists
    if not cookie_file.exists():
        print("❌ cookie.txt not found!")
        print("\nTo update authentication:")
        print("1. Go to music.youtube.com (logged in)")
        print("2. Press F12 → Network tab → Refresh page")
        print("3. Click any request → Request Headers")
        print("4. Copy the entire 'cookie:' value")
        print("5. Paste it into a file named 'cookie.txt'")
        print("6. Run this script again\n")
        return False
    
    # Read cookie from file
    cookie_string = cookie_file.read_text().strip()
    
    if not cookie_string:
        print("❌ cookie.txt is empty!")
        return False
    
    try:
        # Extract SAPISID and generate authorization
        sapisid = extract_sapisid(cookie_string)
        authorization = generate_sapisidhash(sapisid)
        
        # Create browser.json
        browser_data = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Goog-AuthUser": "0",
            "x-origin": "https://music.youtube.com",
            "Cookie": cookie_string,
            "authorization": authorization
        }
        
        # Write to browser.json
        browser_path = Path("browser.json")
        with open(browser_path, 'w') as f:
            json.dump(browser_data, f, indent=2)
        
        print(f"✅ Updated {browser_path}")
        
        # Test authentication
        print("\nTesting authentication...")
        from ytmusicapi import YTMusic
        yt = YTMusic(str(browser_path))
        
        try:
            songs = yt.get_library_songs(limit=1)
            print(f"✅ Authentication works! Found library access.")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
            print("Auth file created but test failed. Try using the server anyway.")
        
        # Clean up cookie.txt for security
        cookie_file.unlink()
        print(f"\n🔒 Deleted {cookie_file} for security")
        
        print("\n🎉 Done! Restart your MCP server to use the new authentication.")
        return True
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you copied the complete cookie string.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🔐 YouTube Music Authentication Updater\n")
    update_auth()
