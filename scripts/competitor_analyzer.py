import urllib.request
import re
from collections import Counter

URLS = [
    "https://cool-events.ro/",
    "https://funevents.ro/",
    "https://momente-magice.ro/"
]
MY_URL = "https://www.superparty.ro/animatori-petreceri-copii"

def get_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def extract_text(html):
    h1s = re.findall(r'<h1.*?>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    h2s = re.findall(r'<h2.*?>(.*?)</h2>', html, re.IGNORECASE | re.DOTALL)
    
    text = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', ' ', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('\n', ' ')
    
    words = re.findall(r'[a-zăâîșț]+', text.lower())
    clean_h1 = [re.sub(r'<.*?>', '', h).strip() for h in h1s]
    clean_h2 = [re.sub(r'<.*?>', '', h).strip() for h in h2s]
    
    return words, clean_h1, clean_h2

stopy = set(['si', 'de', 'in', 'la', 'pe', 'cu', 'pt', 'pentru', 'un', 'o', 'din', 'care', 'sa', 'se', 'au', 'ai', 'ale', 'lor', 'este', 'sunt', 'mai', 'ce', 'ca', 'voi', 'ne', 'le', 'va', 'sau', 'nu', 'noi', 'v', 'a', 'al', 'cum', 'cand', 'unde', 'catre', 'prin', 'pana'])

def get_ngrams(words, n):
    ngrams = []
    for i in range(len(words)-n+1):
        gram = words[i:i+n]
        if not any(w in stopy for w in gram):
            ngrams.append(" ".join(gram))
    return Counter(ngrams)

comp_words = []
comp_h1s = []
comp_h2s = []

for u in URLS:
    h = get_html(u)
    w, h1, h2 = extract_text(h)
    comp_words.extend(w)
    comp_h1s.extend(h1)
    comp_h2s.extend(h2)

my_h = get_html(MY_URL)
my_w, my_h1, my_h2 = extract_text(my_h)

avg_comp_len = len(comp_words) // len(URLS)

out_text = "--- ANALIZA CANTITATIVA PENTRU RANK 1 ---\n"
out_text += f"Media Cuvintelor Competitorilor (Homepages): {avg_comp_len} cuvinte\n"
out_text += f"Numarul de Cuvinte Superparty.ro (Categoria principala): {len(my_w)} cuvinte\n"

if len(my_w) < avg_comp_len:
    out_text += "ALERTA: Avem mai puțin text descresptiv de specialitate pe pagină decât un competitor nativ de locul 1.\n"
else:
    out_text += "AVANTAJ: Volumul nostru de conținut acoperă și depășește media pieței.\n"

out_text += "\n--- IERARHIA TOP COMPETITIE (Ce Titluri folosesc liderii) ---\n"
for h in comp_h1s:
    out_text += f"H1 Inamic: {h[:80].replace('  ', ' ')}\n"

comp_bi = get_ngrams(comp_words, 2).most_common(20)
my_bi = dict(get_ngrams(my_w, 2).most_common(100))

out_text += "\n--- MAPAREA GAP-ULUI (Expresii Semantice Lipsa) ---\n"
out_text += "Iata sintagmele de 2 cuvinte esentiale pe care Liderii le folosesc ca sa stea pe Locul 1, si pe care noi le ignoram:\n"
gap_found = False
for phrase, count in comp_bi:
    target_count = count // len(URLS)
    if target_count < 2: continue # ignore noise
    my_count = my_bi.get(phrase, 0)
    if my_count <= target_count - 2 or my_count == 0:
         out_text += f"GAP CRITIC: '{phrase}' -> Ei o folosesc: {target_count}x | Noi o folosim: {my_count}x\n"
         gap_found = True

if not gap_found:
    out_text += "Site-ul nostru este perfect echipat semantic! Nu avem niciun gol major fata de Competitia Top 3.\n"

with open('reports/seo/competitor_gap.txt', 'w', encoding='utf-8') as f:
    f.write(out_text)

print("Raport generat si salvat in reports/seo/competitor_gap.txt")
