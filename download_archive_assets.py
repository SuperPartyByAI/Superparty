import os
import re
import urllib.request
from bs4 import BeautifulSoup

html_path = r'c:\Users\ursac\WowParty\public\index.html'
public_dir = r'c:\Users\ursac\WowParty\public'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
timestamp = "20240422164712"

print("Scanning for litespeed assets to fetch from archive...")

for link in soup.find_all('link', rel='stylesheet'):
    href = link.get('href', '')
    if '/wp-content/litespeed/css/' in href:
        filename = href.split('?')[0]
        archive_url = f"https://web.archive.org/web/{timestamp}cs_/https://www.wowparty.ro{filename}"
        local_path = os.path.join(public_dir, filename.lstrip('/').replace('/', os.sep))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"⬇️ {filename}")
        try:
            req = urllib.request.Request(archive_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out:
                out.write(response.read())
            print("  ✅ Succes")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

for script in soup.find_all('script'):
    src = script.get('src', '')
    if '/wp-content/litespeed/js/' in src:
        filename = src.split('?')[0]
        archive_url = f"https://web.archive.org/web/{timestamp}js_/https://www.wowparty.ro{filename}"
        local_path = os.path.join(public_dir, filename.lstrip('/').replace('/', os.sep))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        print(f"⬇️ {filename}")
        try:
            req = urllib.request.Request(archive_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out:
                out.write(response.read())
            print("  ✅ Succes")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

print("Gata!")
