import json
from pathlib import Path

manifest = json.loads(Path('reports/seo/indexing_manifest.json').read_text(encoding='utf-8'))
print('=== Remaining indexable entries ===')
for e in manifest:
    if e.get('indexable'):
        print(f"  slug={e.get('slug','?')} | county={e.get('county','')} | type={e.get('place_type','')} | path={e.get('path','')}")
