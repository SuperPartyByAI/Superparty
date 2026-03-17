import os
import sys
import json
import urllib3
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

# Required scopes for sitemap submission
SCOPES = ['https://www.googleapis.com/auth/webmasters']
SITE_URL = 'sc-domain:superparty.ro'
SITEMAP_URL = 'https://www.superparty.ro/sitemap.xml'

env_path = r'C:\Users\ursac\Superparty\.env'
creds_str = None
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('GSC_SERVICE_ACCOUNT_JSON='):
            creds_str = line[len('GSC_SERVICE_ACCOUNT_JSON='):].strip()
            break

if not creds_str:
    print("Could not find GSC credentials in .env file.")
    sys.exit(1)

creds_info = json.loads(creds_str)
creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# Build the Search Console API service
service = build('searchconsole', 'v1', credentials=creds)

try:
    print(f"Submitting sitemap '{SITEMAP_URL}' for site '{SITE_URL}'...")
    response = service.sitemaps().submit(feedpath=SITEMAP_URL, siteUrl=SITE_URL).execute()
    print("Sitemap successfully submitted via API!")
    print(response)
except Exception as e:
    print(f"Failed to submit sitemap: {e}")
