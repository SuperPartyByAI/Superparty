import math
import csv
import time
import requests
from collections import defaultdict

# București (aprox, Piața Unirii)
LAT, LON = 44.4268, 26.1025
RADIUS_M = 100_000  # 100 km

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

PLACE_LOCALITIES = "city|town|village|hamlet|suburb|neighbourhood|locality"

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def overpass_post(query: str, timeout_s=240):
    last_err = None
    for url in OVERPASS_URLS:
        print(f"  Trying: {url}")
        try:
            r = requests.post(url, data={"data": query}, timeout=timeout_s)
            r.raise_for_status()
            print(f"  OK from {url}")
            return r.json()
        except Exception as e:
            last_err = e
            print(f"  FAILED: {e}")
            time.sleep(3)
    raise RuntimeError(f"Overpass failed on all endpoints. Last error: {last_err}")

def fetch_places():
    q = f"""
    [out:json][timeout:180];
    (
      node["place"~"{PLACE_LOCALITIES}"](around:{RADIUS_M},{LAT},{LON});
      way["place"~"{PLACE_LOCALITIES}"](around:{RADIUS_M},{LAT},{LON});
      relation["place"~"{PLACE_LOCALITIES}"](around:{RADIUS_M},{LAT},{LON});
    );
    out center tags;
    """
    return overpass_post(q)

def element_center(el):
    if "lat" in el and "lon" in el:
        return el["lat"], el["lon"]
    c = el.get("center")
    if c and "lat" in c and "lon" in c:
        return c["lat"], c["lon"]
    return None, None

def main():
    print("Fetching places from Overpass API...")
    data = fetch_places()
    rows = []
    seen = set()

    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        place = tags.get("place")
        if not name or not place:
            continue

        lat, lon = element_center(el)
        if lat is None:
            continue

        if haversine_km(LAT, LON, lat, lon) > 100.0:
            continue

        key = (place, name.strip().lower())
        if key in seen:
            continue
        seen.add(key)

        rows.append({
            "place": place,
            "name": name,
            "lat": lat,
            "lon": lon,
            "dist_km": round(haversine_km(LAT, LON, lat, lon), 1),
            "osm_type": el.get("type"),
            "osm_id": el.get("id"),
        })

    rows.sort(key=lambda r: (r["place"], r["name"]))

    counts = defaultdict(int)
    for r in rows:
        counts[r["place"]] += 1

    import os
    os.makedirs("reports/locations", exist_ok=True)
    out_csv = "reports/locations/bucuresti_100km_places.csv"
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["place","name","dist_km","lat","lon","osm_type","osm_id"])
        w.writeheader()
        w.writerows(rows)

    print(f"\nCSV: {out_csv}")
    print(f"TOTAL: {len(rows)}")
    for k in sorted(counts.keys()):
        print(f"  {k}: {counts[k]}")

if __name__ == "__main__":
    main()
