import os
import sys
import glob
import re
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "seo", "uniqueness.config.json")

REPOS = {
    "Superparty": r"C:\Users\ursac\Superparty",
    "WowParty": r"C:\Users\ursac\WowParty",
    "Animatopia": r"C:\Users\ursac\Animatopia",
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: Missing uniqueness.config.json at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_frontmatter(content):
    match = re.search(r"^---\s*(.*?)\s*---", content, re.DOTALL | re.MULTILINE)
    if not match: return {}
    fm_text = match.group(1)
    data = {}
    title_match = re.search(r'title\s*:\s*["\']?(.*?)["\']?\s*$', fm_text, re.MULTILINE)
    if title_match: data['title'] = title_match.group(1).strip()
    return data

def get_body_text(content):
    content = re.sub(r"^---\s*.*?\s*---", "", content, flags=re.DOTALL | re.MULTILINE)
    content = re.sub(r"import\s+.*?;", "", content)
    text = re.sub(r"<[^>]+>", " ", content)
    return re.sub(r"\s+", " ", text).strip().lower()

def jaccard(t1, t2):
    s1, s2 = set(t1.split()), set(t2.split())
    if not s1 or not s2: return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def validate():
    config = load_config()
    max_body_sim = config["thresholds"]["full_page_body_similarity_max"]
    
    pages = []
    
    # 1. Gather all pages
    for site, path in REPOS.items():
        if not os.path.exists(path): continue
        for f in glob.glob(os.path.join(path, "src", "pages", "**", "*.*"), recursive=True):
            if not (f.endswith('.astro') or f.endswith('.mdx') or f.endswith('.md')):
                continue
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            
            # Skip non-indexable pages
            if 'noindex' in content.lower():
                continue
                
            fm = extract_frontmatter(content)
            title = fm.get('title', '')
            body = get_body_text(content)
            pages.append({
                "site": site,
                "path": f,
                "title": title,
                "body": body,
                "content": content
            })
            
    # 2. Check for drafts that are indexable
    errors = []
    for p in pages:
        if 'offline-generation-draft' in p['content'] or 'placeholder' in p['content'].lower():
            errors.append(f"FAIL [Draft/Placeholder is Indexable]: {p['path']}")
            
    # 3. Check for high similarity
    for i in range(len(pages)):
        p1 = pages[i]
        for j in range(i+1, len(pages)):
            p2 = pages[j]
            sim = jaccard(p1['body'], p2['body'])
            if sim > max_body_sim:
                errors.append(f"FAIL [Body Overlap {sim:.2f} > {max_body_sim}]: {p1['path']} <-> {p2['path']}")
                
    if errors:
        print("===")
        print("SEO UNIQUENESS VALIDATOR FAILED")
        print(f"Found {len(errors)} violations across sites.")
        for e in errors[:50]: # print max 50
            print(e)
        if len(errors) > 50:
            print(f"...and {len(errors)-50} more errors.")
        print("===")
        print("Please fix the pages or set them to noindex.")
        sys.exit(1)
    else:
        print("SEO UNIQUENESS VALIDATOR PASSED")
        sys.exit(0)

if __name__ == "__main__":
    validate()
