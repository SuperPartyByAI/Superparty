import json, os, sys, time, urllib.request

# Sincronizare fortata a timpului atomic pentru a pacali desincronizarea Windows-ului (care dadea Invalid JWT Signature)
try:
    print("Sincronizare ceas atomic din memorie...")
    req = urllib.request.urlopen("http://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5)
    data = json.loads(req.read())
    real_time = data["unixtime"]
    diff = real_time - time.time()
    print(f"Ceasul computerului tau era defazat cu {diff} secunde fata de Google. Aplicam peticul temporal...")
    
    orig_time = time.time
    time.time = lambda: orig_time() + diff
except Exception as e:
    print("Nu s-a putut accesa ceasul atomic:", e)

from google.oauth2 import service_account
from googleapiclient.discovery import build
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--site", required=True)
parser.add_argument("--sitemap", required=True)
parser.add_argument("--key", default="service_account.json")
args = parser.parse_args()

SCOPES = ["https://www.googleapis.com/auth/webmasters", "https://www.googleapis.com/auth/indexing"]
creds = service_account.Credentials.from_service_account_file(args.key, scopes=SCOPES)

try:
    indexing = build("indexing", "v3", credentials=creds)
    # The URL to actually index
    url_to_index = "https://www.superparty.ro/animatori-petreceri-copii"
    print("Trimitere URL_UPDATED pe Indexing API catre Google: ", url_to_index)
    body = {"url": url_to_index, "type": "URL_UPDATED"}
    r = indexing.urlNotifications().publish(body=body).execute()
    print("Succes GIGANTIC! Google a primit si aprobat cererea de indexare a URL-ului:")
    print(json.dumps(r, indent=2))
except Exception as e:
    print("Eroare la indexare:", e)
