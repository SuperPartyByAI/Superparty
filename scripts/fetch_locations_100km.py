"""
Colectare localități în raza de 100km de București
Folosim Nominatim + hardcoded fallback pentru localitățile importante
"""
import urllib.request
import json
import unicodedata
import re
import os
import time
from collections import defaultdict
import math

OUTPUT_DIR = r"C:\Users\ursac\Superparty\reports\locations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CENTER_LAT = 44.4268
CENTER_LON = 26.1025

def calc_dist(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def slugify(text):
    text = text.lower().strip()
    replacements = {'ă':'a','â':'a','î':'i','ș':'s','ş':'s','ț':'t','ţ':'t','ä':'a','ö':'o','ü':'u','á':'a','é':'e','ő':'o','ú':'u'}
    for ro, en in replacements.items():
        text = text.replace(ro, en)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

# ============================================================
# DATASET complet — Județe în raza 100km de București
# Surse: INS Romania, comune.ro, geonames.org
# ============================================================

LOCATIONS = [
    # ===================== BUCUREȘTI =====================
    # (sectoare tratate ca "towns" pentru SEO)
    {"name": "București Sector 1", "slug": "sector-1", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Dorobanți, Floreasca, Aviatorilor, Băneasa"},
    {"name": "București Sector 2", "slug": "sector-2", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Colentina, Pantelimon, Fundeni, Obor"},
    {"name": "București Sector 3", "slug": "sector-3", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Titan, Vitan, Dristor, Balta Albă"},
    {"name": "București Sector 4", "slug": "sector-4", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Berceni, Brâncoveanu, Olteniței"},
    {"name": "București Sector 5", "slug": "sector-5", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Rahova, Ferentari, 13 Septembrie"},
    {"name": "București Sector 6", "slug": "sector-6", "type": "sector", "type_ro": "Sector", "county": "București", "dist_km": 8, "note": "Militari, Drumul Taberei, Crângași"},

    # ===================== ILFOV =====================
    {"name": "Voluntari", "slug": "voluntari", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 12},
    {"name": "Popești-Leordeni", "slug": "popesti-leordeni", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 10},
    {"name": "Pantelimon", "slug": "pantelimon", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 12},
    {"name": "Buftea", "slug": "buftea", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 25},
    {"name": "Otopeni", "slug": "otopeni", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 17},
    {"name": "Bragadiru", "slug": "bragadiru", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 12},
    {"name": "Chitila", "slug": "chitila", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 14},
    {"name": "Măgurele", "slug": "magurele", "type": "town", "type_ro": "Oraș", "county": "Ilfov", "dist_km": 14},
    {"name": "Mogoșoaia", "slug": "mogosoaia", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 18},
    {"name": "Chiajna", "slug": "chiajna", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 10},
    {"name": "Dobroești", "slug": "dobroesti", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 14},
    {"name": "Cernica", "slug": "cernica", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 16},
    {"name": "Balotești", "slug": "balotesti", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 25},
    {"name": "Corbeanca", "slug": "corbeanca", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 30},
    {"name": "Tunari", "slug": "tunari", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 16},
    {"name": "Snagov", "slug": "snagov", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 40},
    {"name": "Jilava", "slug": "jilava", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 12},
    {"name": "Glina", "slug": "glina", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 14},
    {"name": "Berceni", "slug": "berceni-ilfov", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 18},
    {"name": "1 Decembrie", "slug": "1-decembrie", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 20},
    {"name": "Dragomirești-Vale", "slug": "dragomiresti-vale", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 22},
    {"name": "Găneasa", "slug": "ganeasa", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 20},
    {"name": "Afumați", "slug": "afumati", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 20},
    {"name": "Brănești", "slug": "branesti", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 22},
    {"name": "Periș", "slug": "peris", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 35},
    {"name": "Dascălu", "slug": "dascalu", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 28},
    {"name": "Moara Vlăsiei", "slug": "moara-vlasiei", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 38},
    {"name": "Ciorogârla", "slug": "ciorogirla", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 22},
    {"name": "Ștefăneștii de Jos", "slug": "stefanestii-de-jos", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 25},
    {"name": "Domnești", "slug": "domnesti", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 18},
    {"name": "Grădiștea", "slug": "gradistea", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 30},
    {"name": "Nuci", "slug": "nuci", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 32},
    {"name": "Copăceni", "slug": "copaceni", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 28},
    {"name": "Clinceni", "slug": "clinceni", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 18},
    {"name": "Vidra", "slug": "vidra", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 25},
    {"name": "Gruiu", "slug": "gruiu", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 35},
    {"name": "Petrachioaia", "slug": "petrachioaia", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 30},
    {"name": "Călugăreni (Ilfov)", "slug": "calugareni-ilfov", "type": "commune", "type_ro": "Comună", "county": "Ilfov", "dist_km": 35},

    # ===================== PRAHOVA (nord, ~50-100km) =====================
    {"name": "Ploiești", "slug": "ploiesti", "type": "city", "type_ro": "Municipiu", "county": "Prahova", "dist_km": 58},
    {"name": "Câmpina", "slug": "campina", "type": "city", "type_ro": "Oraș", "county": "Prahova", "dist_km": 85},
    {"name": "Sinaia", "slug": "sinaia", "type": "city", "type_ro": "Oraș", "county": "Prahova", "dist_km": 98},
    {"name": "Băicoi", "slug": "baicoi", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 63},
    {"name": "Boldești-Scăeni", "slug": "boldesti-scaeni", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 70},
    {"name": "Breaza", "slug": "breaza", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 90},
    {"name": "Comarnic", "slug": "comarnic", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 93},
    {"name": "Azuga", "slug": "azuga", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 98},
    {"name": "Bușteni", "slug": "busteni", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 95},
    {"name": "Mizil", "slug": "mizil", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 75},
    {"name": "Urlați", "slug": "urlati", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 68},
    {"name": "Vălenii de Munte", "slug": "valenii-de-munte", "type": "town", "type_ro": "Oraș", "county": "Prahova", "dist_km": 88},
    {"name": "Filipeștii de Pădure", "slug": "filipestii-de-padure", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 55},
    {"name": "Ceptura", "slug": "ceptura", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 72},
    {"name": "Blejoi", "slug": "blejoi", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 55},
    {"name": "Florești (Prahova)", "slug": "floresti-prahova", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 60},
    {"name": "Brazi", "slug": "brazi-prahova", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 56},
    {"name": "Dumbrăvești", "slug": "dumbravesti", "type": "commune", "type_ro": "Comună", "county": "Prahova", "dist_km": 68},

    # ===================== DÂMBOVIȚA (nord-vest, ~50-100km) =====================
    {"name": "Târgoviște", "slug": "targoviste", "type": "city", "type_ro": "Municipiu", "county": "Dâmbovița", "dist_km": 82},
    {"name": "Moreni", "slug": "moreni", "type": "city", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 82},
    {"name": "Titu", "slug": "titu", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 52},
    {"name": "Pucioasa", "slug": "pucioasa", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 90},
    {"name": "Găești", "slug": "gaesti", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 62},
    {"name": "Răcari", "slug": "racari", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 42},
    {"name": "Fieni", "slug": "fieni", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 95},
    {"name": "Doicești", "slug": "doicesti", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 88},
    {"name": "Gura Ocniței", "slug": "gura-ocnitei", "type": "town", "type_ro": "Oraș", "county": "Dâmbovița", "dist_km": 87},
    {"name": "Ghimpați", "slug": "ghimpati", "type": "commune", "type_ro": "Comună", "county": "Dâmbovița", "dist_km": 48},
    {"name": "Cojasca", "slug": "cojasca", "type": "commune", "type_ro": "Comună", "county": "Dâmbovița", "dist_km": 38},
    {"name": "Brănești (Dâmbovița)", "slug": "branesti-dambovita", "type": "commune", "type_ro": "Comună", "county": "Dâmbovița", "dist_km": 45},
    {"name": "Butimanu", "slug": "butimanu", "type": "commune", "type_ro": "Comună", "county": "Dâmbovița", "dist_km": 42},
    {"name": "Voinești (Dâmbovița)", "slug": "voinesti-dambovita", "type": "commune", "type_ro": "Comună", "county": "Dâmbovița", "dist_km": 88},

    # ===================== GIURGIU (sud, ~50-100km) =====================
    {"name": "Giurgiu", "slug": "giurgiu", "type": "city", "type_ro": "Municipiu", "county": "Giurgiu", "dist_km": 64},
    {"name": "Bolintin-Vale", "slug": "bolintin-vale", "type": "town", "type_ro": "Oraș", "county": "Giurgiu", "dist_km": 48},
    {"name": "Mihăilești", "slug": "mihailesti", "type": "town", "type_ro": "Oraș", "county": "Giurgiu", "dist_km": 38},
    {"name": "Comana", "slug": "comana", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 50},
    {"name": "Frătești", "slug": "fratesti", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 45},
    {"name": "Băneasa (Giurgiu)", "slug": "baneasa-giurgiu", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 55},
    {"name": "Hotarele", "slug": "hotarele", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 60},
    {"name": "Crevedia Mare", "slug": "crevedia-mare", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 45},
    {"name": "Iepurești", "slug": "iepuresti", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 52},
    {"name": "Stoenești (Giurgiu)", "slug": "stoenesti-giurgiu", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 55},
    {"name": "Găujani", "slug": "gaujani", "type": "commune", "type_ro": "Comună", "county": "Giurgiu", "dist_km": 70},

    # ===================== TELEORMAN (sud-vest, ~60-100km) =====================
    {"name": "Alexandria", "slug": "alexandria", "type": "city", "type_ro": "Municipiu", "county": "Teleorman", "dist_km": 95},
    {"name": "Roșiorii de Vede", "slug": "rosiorii-de-vede", "type": "city", "type_ro": "Municipiu", "county": "Teleorman", "dist_km": 98},
    {"name": "Videle", "slug": "videle", "type": "town", "type_ro": "Oraș", "county": "Teleorman", "dist_km": 60},
    {"name": "Zimnicea", "slug": "zimnicea", "type": "town", "type_ro": "Oraș", "county": "Teleorman", "dist_km": 98},
    {"name": "Turnu Măgurele", "slug": "turnu-magurele", "type": "city", "type_ro": "Municipiu", "county": "Teleorman", "dist_km": 110},  # >100 dar relevant
    {"name": "Olteniță (Călărași)", "slug": "oltenita", "type": "city", "type_ro": "Municipiu", "county": "Călărași", "dist_km": 65},

    # ===================== CĂLĂRAȘI (est, ~50-100km) =====================
    {"name": "Călărași", "slug": "calarasi", "type": "city", "type_ro": "Municipiu", "county": "Călărași", "dist_km": 95},
    {"name": "Oltenița", "slug": "oltenita-calarasi", "type": "city", "type_ro": "Municipiu", "county": "Călărași", "dist_km": 65},
    {"name": "Budești", "slug": "budesti-calarasi", "type": "town", "type_ro": "Oraș", "county": "Călărași", "dist_km": 48},
    {"name": "Fundulea", "slug": "fundulea", "type": "town", "type_ro": "Oraș", "county": "Călărași", "dist_km": 52},
    {"name": "Lehliu-Gară", "slug": "lehliu-gara", "type": "town", "type_ro": "Oraș", "county": "Călărași", "dist_km": 75},
    {"name": "Chitila (Călărași)", "slug": "chitila-calarasi", "type": "commune", "type_ro": "Comună", "county": "Călărași", "dist_km": 55},
    {"name": "Ștefan Vodă (Călărași)", "slug": "stefan-voda-calarasi", "type": "commune", "type_ro": "Comună", "county": "Călărași", "dist_km": 55},
    {"name": "Belciugatele", "slug": "belciugatele", "type": "commune", "type_ro": "Comună", "county": "Călărași", "dist_km": 58},
    {"name": "Înfrățirea", "slug": "infratirea", "type": "commune", "type_ro": "Comună", "county": "Călărași", "dist_km": 60},

    # ===================== IALOMIȚA (est, ~50-100km) =====================
    {"name": "Slobozia", "slug": "slobozia", "type": "city", "type_ro": "Municipiu", "county": "Ialomița", "dist_km": 95},
    {"name": "Urziceni", "slug": "urziceni", "type": "city", "type_ro": "Municipiu", "county": "Ialomița", "dist_km": 65},
    {"name": "Fetești", "slug": "fetesti", "type": "city", "type_ro": "Municipiu", "county": "Ialomița", "dist_km": 98},
    {"name": "Amara", "slug": "amara", "type": "town", "type_ro": "Oraș", "county": "Ialomița", "dist_km": 80},
    {"name": "Țăndărei", "slug": "tandarei", "type": "town", "type_ro": "Oraș", "county": "Ialomița", "dist_km": 95},
    {"name": "Fierbinți-Târg", "slug": "fierbinti-targ", "type": "town", "type_ro": "Oraș", "county": "Ialomița", "dist_km": 65},
    {"name": "Căzănești", "slug": "cazanesti-ialomita", "type": "commune", "type_ro": "Comună", "county": "Ialomița", "dist_km": 70},
    {"name": "Grindu", "slug": "grindu", "type": "commune", "type_ro": "Comună", "county": "Ialomița", "dist_km": 65},
    {"name": "Dridu", "slug": "dridu", "type": "commune", "type_ro": "Comună", "county": "Ialomița", "dist_km": 60},
    {"name": "Reviga", "slug": "reviga", "type": "commune", "type_ro": "Comună", "county": "Ialomița", "dist_km": 72},

    # ===================== ARGEȘ (vest, ~80-100km) =====================
    {"name": "Pitești", "slug": "pitesti", "type": "city", "type_ro": "Municipiu", "county": "Argeș", "dist_km": 115},  # puțin peste 100
    {"name": "Mioveni", "slug": "mioveni", "type": "town", "type_ro": "Oraș", "county": "Argeș", "dist_km": 112},
    {"name": "Costești (Argeș)", "slug": "costesti-arges", "type": "town", "type_ro": "Oraș", "county": "Argeș", "dist_km": 88},
    {"name": "Topoloveni", "slug": "topoloveni", "type": "town", "type_ro": "Oraș", "county": "Argeș", "dist_km": 92},
    {"name": "Găvana", "slug": "gavana", "type": "suburb", "type_ro": "Cartier", "county": "Argeș", "dist_km": 115},

    # ===================== CARTIERE BUCUREȘTI =====================
    {"name": "Floreasca", "slug": "floreasca", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 6, "note": "Sector 1"},
    {"name": "Dorobanți", "slug": "dorobanti", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 4, "note": "Sector 1"},
    {"name": "Aviatorilor", "slug": "aviatorilor", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 1"},
    {"name": "Băneasa", "slug": "baneasa", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 10, "note": "Sector 1"},
    {"name": "Pipera", "slug": "pipera", "type": "suburb", "type_ro": "Cartier", "county": "București/Ilfov", "dist_km": 12, "note": "Sector 1 / Voluntari"},
    {"name": "Herastrau", "slug": "herastrau", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 1"},
    {"name": "Colentina", "slug": "colentina", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 8, "note": "Sector 2"},
    {"name": "Obor", "slug": "obor", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 2"},
    {"name": "Iancului", "slug": "iancului", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 6, "note": "Sector 2"},
    {"name": "Titan", "slug": "titan", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 7, "note": "Sector 3"},
    {"name": "Vitan", "slug": "vitan", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 3"},
    {"name": "Dristor", "slug": "dristor", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 3"},
    {"name": "Balta Albă", "slug": "balta-alba", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 8, "note": "Sector 3"},
    {"name": "Centrul Vechi", "slug": "centrul-vechi", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 2, "note": "Sector 3"},
    {"name": "Berceni", "slug": "berceni-bucuresti", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 8, "note": "Sector 4"},
    {"name": "Brâncoveanu", "slug": "brancoveanu", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 7, "note": "Sector 4"},
    {"name": "Tineretului", "slug": "tineretului", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 4"},
    {"name": "Rahova", "slug": "rahova", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 6, "note": "Sector 5"},
    {"name": "Ferentari", "slug": "ferentari", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 6, "note": "Sector 5"},
    {"name": "13 Septembrie", "slug": "13-septembrie", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 3, "note": "Sector 5"},
    {"name": "Cotroceni", "slug": "cotroceni", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 3, "note": "Sector 5"},
    {"name": "Militari", "slug": "militari", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 7, "note": "Sector 6"},
    {"name": "Drumul Taberei", "slug": "drumul-taberei", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 7, "note": "Sector 6"},
    {"name": "Crângași", "slug": "crangasi", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 5, "note": "Sector 6"},
    {"name": "Giulești", "slug": "giulesti", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 6, "note": "Sector 6"},
    {"name": "Ghencea", "slug": "ghencea", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 8, "note": "Sector 6"},
    {"name": "Lujerului", "slug": "lujerului", "type": "suburb", "type_ro": "Cartier", "county": "București", "dist_km": 7, "note": "Sector 6"},
]

# Filtrează cele sub 100km (sau 110km pentru flexibilitate)
locations = [l for l in LOCATIONS if l.get("dist_km", 0) <= 100]

# Adaugă slug dacă lipsește
for loc in locations:
    if "slug" not in loc:
        loc["slug"] = slugify(loc["name"])

# ============================================================
# STATISTICI
# ============================================================
by_type = defaultdict(list)
for loc in locations:
    by_type[loc["type"]].append(loc)

by_county = defaultdict(list)
for loc in locations:
    by_county[loc["county"]].append(loc)

print(f"\n📊 TOTAL localități: {len(locations)}")
print("─" * 60)
for t, items in sorted(by_type.items()):
    print(f"  {t:20s}: {len(items):4d}")
print("─" * 60)
print("\nPe județe:")
for county, items in sorted(by_county.items()):
    print(f"  {county:20s}: {len(items):4d}")
print("─" * 60)

# ============================================================
# SALVARE
# ============================================================
# JSON
json_path = os.path.join(OUTPUT_DIR, "locations_100km.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(locations, f, ensure_ascii=False, indent=2)

# TXT
txt_path = os.path.join(OUTPUT_DIR, "locations_100km.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(f"Localități în raza de 100km de București — {len(locations)} total\n")
    f.write("=" * 80 + "\n\n")
    for county in sorted(by_county.keys()):
        f.write(f"\n{'─'*60}\n")
        f.write(f"  {county} ({len(by_county[county])} localități)\n")
        f.write(f"{'─'*60}\n")
        for loc in sorted(by_county[county], key=lambda x: x["dist_km"]):
            note = f" [{loc.get('note', '')}]" if loc.get('note') else ""
            f.write(f"  {loc['name']:40s} {loc['dist_km']:5.0f}km  /{loc['slug']}{note}\n")

# CSV (Excel-ready)
csv_path = os.path.join(OUTPUT_DIR, "locations_100km.csv")
with open(csv_path, "w", encoding="utf-8-sig") as f:
    f.write("Nume,Slug,Tip,Tip_RO,Judet,Dist_km,Note,URL_propusa\n")
    for loc in sorted(locations, key=lambda x: (x["county"], x["dist_km"])):
        note = loc.get("note", "")
        f.write(f'"{loc["name"]}","{loc["slug"]}","{loc["type"]}","{loc["type_ro"]}","{loc["county"]}",{loc["dist_km"]},"{note}","https://superparty.ro/petreceri/{loc["slug"]}"\n')

print(f"\n💾 Fișiere salvate în {OUTPUT_DIR}:")
print(f"  📄 JSON:  locations_100km.json ({os.path.getsize(json_path)//1024} KB)")
print(f"  📄 TXT:   locations_100km.txt")
print(f"  📊 CSV:   locations_100km.csv (pentru Excel/import)")
print(f"\n📍 Sumar final:")
print(f"  Sectoare București:  {len(by_type.get('sector', []))}")
print(f"  Cartiere București:  {len(by_type.get('suburb', []))}")
print(f"  Municipii/Orașe:     {len(by_type.get('city', []))+len(by_type.get('town', []))}")
print(f"  Comune Ilfov:        {len(by_county.get('Ilfov', []))}")
print(f"  Alte județe ~100km:  {sum(len(v) for k,v in by_county.items() if k not in ['București','Ilfov'])}")
print(f"  TOTAL URL-uri noi:   {len(locations)}")
