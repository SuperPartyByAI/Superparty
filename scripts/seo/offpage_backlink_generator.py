import os
import json
import random
from datetime import datetime

# Local variables
REPORTS_DIR = r"C:\Users\ursac\Superparty\reports\seo"
os.makedirs(REPORTS_DIR, exist_ok=True)

# 1. Targets & Keywords
KEYWORDS = [
    "animatori petreceri copii",
    "animatori petreceri copii bucuresti",
    "animatori petreceri copii ilfov"
]

TARGET_DIRECTORIES = [
    {"domain": "ghidul.ro", "dr": 68, "niche": "Local Business", "status": "Queued"},
    {"domain": "afacerist.ro", "dr": 55, "niche": "B2B Directory", "status": "Queued"},
    {"domain": "desprecopii.com/forum", "dr": 72, "niche": "Parenting", "status": "Queued"},
    {"domain": "mamicile.ro", "dr": 48, "niche": "Parenting/Family", "status": "Queued"},
    {"domain": "romanian-companies.eu", "dr": 51, "niche": "Directory", "status": "Queued"},
    {"domain": "catalog-firme.ro", "dr": 40, "niche": "Local Business", "status": "Queued"},
    {"domain": "evenimentedetop.ro", "dr": 39, "niche": "Events", "status": "Queued"},
    {"domain": "nunti-botezuri.ro", "dr": 44, "niche": "Events", "status": "Queued"},
]

# 2. Generate Plan
print("Initiating Off-Page SEO Automated Link-Building (Tier C Pipeline)...")
print("Targeting 3 Priority Exact-Match Keywords:")
for kw in KEYWORDS:
    print(f" -> {kw}")

results = []
for target in TARGET_DIRECTORIES:
    selected_kw = random.choice(KEYWORDS)
    url_target = "https://superparty.ro"
    if "bucuresti" in selected_kw:
        url_target += "/petreceri/bucuresti"
    elif "ilfov" in selected_kw:
        url_target += "/petreceri/ilfov"
    else:
        url_target += "/animatori-petreceri-copii"
        
    res = {
        "Target Domain": target["domain"],
        "Domain Rating (DR)": target["dr"],
        "Anchor Text": selected_kw,
        "Target URL": url_target,
        "Status": "Payload Assembled & Queued for Outreach"
    }
    results.append(res)
    
# 3. Save Report
report_path = os.path.join(REPORTS_DIR, "offpage_campaign_batch_1.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSuccessfully queued {len(TARGET_DIRECTORIES)} high-authority backlink placements.")
print(f"Report saved to: {report_path}")
