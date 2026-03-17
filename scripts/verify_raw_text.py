import os
import re
import math
from collections import Counter

def get_clean_text(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Try to extract <main> content
        main_match = re.search(r'<main[^>]*>(.*?)</main>', html, flags=re.IGNORECASE | re.DOTALL)
        if main_match:
            html = main_match.group(1)
        else:
            # Fallback: remove header, nav, footer
            html = re.sub(r'<(header|nav|footer)[^>]*>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
            
        # Remove scripts and styles
        html = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        
        words = re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ]+', text.lower())
        stop_words = {'și', 'în', 'de', 'la', 'cu', 'o', 'un', 'pe', 'că', 'să', 'din', 'pentru', 'care', 'este', 'a', 'al', 'ai', 'ale', 'se', 'au', 'sunt', 'mai', 'vor', 'vorba', 'fie', 'vă', 'ne', 'vrem', 'îi', 'dacă', 'până'}
        return [w for w in words if w not in stop_words and len(w) > 2]
    except Exception as e:
        print(f'Error reading {filepath}: {e}')
        return []

def get_similarity(w1, w2):
    c1, c2 = Counter(w1), Counter(w2)
    intersection = set(c1.keys()) & set(c2.keys())
    numerator = sum(c1[x] * c2[x] for x in intersection)
    sum1 = sum(c1[x]**2 for x in c1.keys())
    sum2 = sum(c2[x]**2 for x in c2.keys())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator: return 0.0
    return numerator / denominator

base_dist = r'C:\Users\ursac\Superparty\dist'

print('=== DOM RAW TEXT SIMILARITY ===')

# 1. Test Spoke Pages (Batman S1 vs S4)
spoke1 = os.path.join(base_dist, 'petreceri', 'animatori-petreceri-copii-batman-sector-1', 'index.html')
spoke2 = os.path.join(base_dist, 'petreceri', 'animatori-petreceri-copii-batman-sector-4', 'index.html')

if os.path.exists(spoke1) and os.path.exists(spoke2):
    w1, w2 = get_clean_text(spoke1), get_clean_text(spoke2)
    sim = get_similarity(w1, w2)
    print(f'Spoke Uniqueness (Batman S1 vs S4): {(1 - sim) * 100:.2f}%')
    print(f'Pure Words Count: {len(w1)} vs {len(w2)}')
else:
    print('Spoke dist files not found. Ensure "npm run build" completed.')

# 2. Test Hub Pages (Sector 1 vs Voluntari)
hub1 = os.path.join(base_dist, 'animatori-copii-sector-1', 'index.html')
hub2 = os.path.join(base_dist, 'animatori-copii-voluntari', 'index.html')

if os.path.exists(hub1) and os.path.exists(hub2):
    w1, w2 = get_clean_text(hub1), get_clean_text(hub2)
    sim = get_similarity(w1, w2)
    print(f'Hub Uniqueness (Sector 1 vs Voluntari): {(1 - sim) * 100:.2f}%')
    print(f'Pure Words Count: {len(w1)} vs {len(w2)}')
else:
    print('Hub dist files not found.')
