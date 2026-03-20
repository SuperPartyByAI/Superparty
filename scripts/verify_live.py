import urllib.request
import re
from collections import Counter

LIVE_URL = "https://www.superparty.ro/"

print(f"--- INITIAZA ATACUL DE VALIDARE PE SERVERELE VERCEL: {LIVE_URL} ---")
print("   (Acesta e fix ce citeste Googlebot chiar in secunda asta!)\n")

req = urllib.request.Request(LIVE_URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Scoatem script-uri, stiluri
text = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
text = re.sub(r'<.*?>', ' ', text)
text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('\n', ' ')

text_lower = text.lower()

# Numaram cuvintele romanesti
words = re.findall(r'[a-zăâîșț]+', text_lower)
word_count = len(words)

# Fraze tinta GAP
phrases = [
  "copilul tau",
  "copii bucuresti",
  "orice petrecere",
  "petreceri copii",
  "vata de zahar",
  "popcorn",
  "baloane cu heliu",
  "arcada baloane"
]

def normalize(s):
    return s.replace('ă', 'a').replace('â', 'a').replace('î', 'i').replace('ș', 's').replace('ț', 't')

norm_text = normalize(text_lower)

print("==================================================")
print("REZULTAT OFICIAL (LIVE WEB SCRAPER)")
print("==================================================")
print(f"Numar Cuvinte pe Prima Pagina: {word_count} cuvinte!")
if word_count > 1627:
    print("   [SUCCES]: SUPERPARTY.RO l-a depasit in greutate pe Liderul National (care are 1627).")
else:
    print(f"   [ALERTA]: Sub 1627 cuvinte (are {word_count}).")

print("\nFRECVENTA EXPRESIILOR DE GAP (Topical SEO):")
for p in phrases:
    np = normalize(p)
    count = len(re.findall(r'\b' + re.escape(np) + r'\b', norm_text))
    print(f" - [{p.upper()}]: a fost gasit de {count} ori in cod.")

magician_count = len(re.findall(r'\bmagician', norm_text))
print(f"\nTest Anti-Spam (Magician): gasit de {magician_count} ori.")
print("==================================================")
