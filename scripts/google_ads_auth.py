#!/usr/bin/env python3
"""google_ads_auth.py - Interactive OAuth2 flow to get Google Ads refresh token.

Run this ONCE locally (or on server with terminal) to generate GOOGLE_ADS_REFRESH_TOKEN.
Then store the token in GitHub Secrets.

Usage:
    GOOGLE_ADS_CLIENT_ID=... GOOGLE_ADS_CLIENT_SECRET=... python3 scripts/google_ads_auth.py
"""
import os
import urllib.parse
import urllib.request
import json
import webbrowser

CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Set GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET in env")
    exit(1)

REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"  # out-of-band (console)
SCOPE = "https://www.googleapis.com/auth/adwords"

auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    + urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    })
)

print("\n== Google Ads OAuth2 Authorization ==")
print("\n1. Open this URL in your browser:")
print(f"   {auth_url}")
print("\n2. Authorize the app, then copy the authorization code.")

try:
    webbrowser.open(auth_url)
except Exception:
    pass

code = input("\n3. Paste the authorization code here: ").strip()

# Exchange code for tokens
data = urllib.parse.urlencode({
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": REDIRECT_URI,
    "grant_type": "authorization_code",
}).encode()

req = urllib.request.Request(
    "https://oauth2.googleapis.com/token", data=data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
resp = json.loads(urllib.request.urlopen(req, timeout=15).read())

refresh_token = resp.get("refresh_token", "")
access_token = resp.get("access_token", "")

print("\n== RESULTS ==")
if refresh_token:
    print(f"GOOGLE_ADS_REFRESH_TOKEN={refresh_token}")
    print("\nAdd this to GitHub Secrets and .env.agent:")
    print(f"  gh secret set GOOGLE_ADS_REFRESH_TOKEN --repo=SuperPartyByAI/Superparty")
    print(f"  echo \'GOOGLE_ADS_REFRESH_TOKEN={refresh_token}\' >> /srv/superparty/.env.agent")
else:
    print("ERROR: No refresh_token in response:", resp)
