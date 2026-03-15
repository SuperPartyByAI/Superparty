"""Quick Supabase connection test."""
import json, base64, os, sys, pathlib, urllib.request, urllib.error

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parent.parent / ".env", override=True)
except ImportError:
    pass

url = os.environ.get("SUPABASE_URL", "")
key = os.environ.get("SUPABASE_KEY", "")

print(f"URL: {url}")
print(f"KEY length: {len(key)}")
print(f"KEY first 50: {key[:50]}")
print(f"KEY last 10: {key[-10:]}")

# Decode JWT payload
try:
    parts = key.split(".")
    payload = parts[1] + "==" * (4 - len(parts[1]) % 4)
    d = json.loads(base64.b64decode(payload))
    print(f"JWT role: {d.get('role', 'MISSING')}")
    print(f"JWT ref: {d.get('ref', 'MISSING')}")
    print(f"JWT iss: {d.get('iss', 'MISSING')}")
except Exception as e:
    print(f"JWT decode error: {e}")

# Test API call
endpoint = f"{url}/rest/v1/sites?select=domain&order=domain&limit=3"
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Accept": "application/json",
}
req = urllib.request.Request(endpoint, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"\nSUCCESS: {len(data)} sites returned")
        for s in data:
            print(f"  - {s['domain']}")
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ""
    print(f"\nERROR {e.code}: {body}")
