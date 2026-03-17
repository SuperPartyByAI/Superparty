import os
import glob
import json
import re

db_path = r'C:\Users\ursac\Superparty\scripts\local_db.json'
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

regions = db['regions']
reviews = db['reviews']

base_content = r'C:\Users\ursac\Superparty\src\content\petreceri'
mdx_files = glob.glob(os.path.join(base_content, '**', '*.mdx'), recursive=True) + glob.glob(os.path.join(base_content, '**', '*.md'), recursive=True)

print(f"Found {len(mdx_files)} spoke pages to process.")

MARKER = '<!-- LOCAL_INJECT_START -->'
injected_count = 0

for filepath in mdx_files:
    filename = os.path.basename(filepath).lower()
    
    matched_region = None
    for reg_key in regions.keys():
        if reg_key in filename:
            matched_region = reg_key
            break
            
    if not matched_region:
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if MARKER in content:
        continue

    region_data = regions[matched_region]
    
    parks_str = ', '.join(region_data['parks'])
    vibe_para = f"\n\n{MARKER}\n\n### Super Distracție în Zona Ta\n\nFie că organizați evenimentul la curte, în spații generoase precum {parks_str}, sau într-un cadru mai restrâns, personajele noastre aduc bucuria direct la voi! Echipa Superparty cunoaște foarte bine această zonă, adaptând jocurile și recuzita pentru specificul locațiilor: {region_data['vibe']}."
    
    faq_para = '\n\n### Întrebări Frecvente Locale\n'
    for faq in region_data['faqs']:
        faq_para += f"\n**{faq['q']}**\n{faq['a']}\n"
        
    local_revs = [r for r in reviews if r['location_tag'] == matched_region or r['location_tag'] in ['bucuresti', 'ilfov']]
    
    rev_para = f'\n\n### Părerea Părinților ({matched_region.replace("-", " ").title()})\n'
    for rev in local_revs[:2]:
        author_clean = rev['author'] if matched_region in rev.get('location_tag', '') else rev['author']
        rev_para += f"\n> \"{rev['text']}\" — **{author_clean}**\n"
        
    injection = vibe_para + faq_para + rev_para + '\n<!-- LOCAL_INJECT_END -->\n'
    
    inject_point = content.rfind('## ')
    if inject_point == -1 or inject_point < len(content) // 2:
        new_content = content + injection
    else:
        new_content = content[:inject_point] + injection + '\n' + content[inject_point:]
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    injected_count += 1

print(f"Successfully injected hyper-local context into {injected_count} Spoke pages.")
