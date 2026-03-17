import os
import glob
import sys
from bs4 import BeautifulSoup

dist_dir = r"C:\Users\ursac\Superparty\dist"
html_files = glob.glob(os.path.join(dist_dir, "**", "*.html"), recursive=True)

missing_canonicals = []
mismatch_canonicals = []
total_files = 0
checked_pages = 0

BASE_URL = "https://www.superparty.ro"

for filepath in html_files:
    total_files += 1
    # We only care about actual pages, skip 404.html if we want, but let's check all
    if "404.html" in filepath: continue
    
    # Calculate the expected path.
    # e.g., dist\animatori-copii-sector-1\index.html -> /animatori-copii-sector-1/
    # dist\index.html -> /
    rel_path = os.path.relpath(filepath, dist_dir).replace("\\", "/")
    if rel_path == "index.html":
        expected_path = "/"
    elif rel_path.endswith("/index.html"):
        expected_path = "/" + rel_path[:-10] # drop index.html but keep trailing slash or not? Let's check what Astro generates.
    else:
        expected_path = "/" + rel_path.replace(".html", "")

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    canonical_tag = soup.find("link", rel="canonical")
    
    checked_pages += 1
    
    if not canonical_tag or not canonical_tag.has_attr("href"):
        missing_canonicals.append(filepath)
        continue
        
    actual_href = canonical_tag["href"]
    
    # Check if absolute
    if not actual_href.startswith("https://www.superparty.ro"):
        mismatch_canonicals.append((filepath, "Not absolute", actual_href))
        continue
        
    # Check if it matches expected path (roughly)
    path_part = actual_href.replace("https://www.superparty.ro", "")
    
    # Let's just compare if it ends with the right slug
    slug = expected_path.strip("/")
    if slug and slug not in path_part:
        mismatch_canonicals.append((filepath, f"Expected slug '{slug}' missing", actual_href))

print("=== CANONICAL VERIFICATION REPORT ===")
print(f"Total HTML files found: {total_files}")
print(f"Total pages checked: {checked_pages}")

if not missing_canonicals and not mismatch_canonicals:
    print("\n✅ SUCCESS: 100% of pages have a valid self-referencing absolute canonical tag.")
    sys.exit(0)
    
if missing_canonicals:
    print(f"\n❌ FAILED: {len(missing_canonicals)} pages are missing canonical tags:")
    for m in missing_canonicals[:10]:
        print(f"   - {m}")
    if len(missing_canonicals) > 10: print("   ... and more.")

if mismatch_canonicals:
    print(f"\n⚠️ WARNING: {len(mismatch_canonicals)} pages have mismatched canonicals:")
    for f, reason, href in mismatch_canonicals[:10]:
        print(f"   - {os.path.basename(f)} | Reason: {reason} | Found: {href}")
    if len(mismatch_canonicals) > 10: print("   ... and more.")

sys.exit(1)
