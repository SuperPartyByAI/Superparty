import urllib.request
import re
import json

urls = [
    'https://animatopia.ro/',
    'https://animatopia.ro/animatori-petreceri-copii/',
    'https://www.superparty.ro/'
]

res = []
for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            headers = response.headers
            
            x_robots = headers.get('X-Robots-Tag')
            meta_robots = re.findall(r'<meta[^>]*name=[\"\'\']robots[\"\'\'][^>]*>', html, re.I)
            can = re.findall(r'<link[^>]*rel=[\"\'\']canonical[\"\'\'][^>]*>', html, re.I)
            
            res.append({
                'url': u,
                'x_robots_tag': x_robots,
                'meta_robots': meta_robots[0] if meta_robots else None,
                'canonical': can[0] if can else None
            })
    except Exception as e:
        res.append({'url': u, 'error': str(e)})

with open('C:/Users/ursac/Superparty/reports/seo_check.json', 'w') as f:
    json.dump(res, f, indent=2)
