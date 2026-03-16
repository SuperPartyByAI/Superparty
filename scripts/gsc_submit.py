import json, os, sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Usage:
# python scripts/gsc_submit.py --site https://animatopia.ro --sitemap https://animatopia.ro/sitemap-index.xml --key service_account.json

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--site", required=True)
parser.add_argument("--sitemap", required=True)
parser.add_argument("--key", default="service_account.json")
args = parser.parse_args()

SCOPES = ["https://www.googleapis.com/auth/webmasters", "https://www.googleapis.com/auth/indexing"]

creds = service_account.Credentials.from_service_account_file(args.key, scopes=SCOPES)

# Submit sitemap via Search Console (webmasters) API
webmasters = build("webmasters", "v3", credentials=creds)
print("Submitting sitemap:", args.sitemap, "for site:", args.site)
resp = webmasters.sitemaps().submit(siteUrl=args.site, feedpath=args.sitemap).execute()
print("Sitemap submit response:", resp)

# Indexing API (URL_UPDATED) — only if eligible
try:
    indexing = build("indexing", "v3", credentials=creds)
    url = args.sitemap  # or owner page URL
    print("Sending URL_UPDATED notification for sitemap (or owner page) ...")
    body = {"url": args.sitemap, "type": "URL_UPDATED"}
    r = indexing.urlNotifications().publish(body=body).execute()
    print("Indexing API response:", r)
except Exception as e:
    print("Indexing API call failed or not eligible:", e)
