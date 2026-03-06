import os
import glob
from pathlib import Path

scripts = glob.glob(r'REPO_ROOT\scripts\*.py')

for s in scripts:
    with open(s, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Check if from pathlib import Path is there
    if 'from pathlib import Path' not in content:
        content = "import os\nfrom pathlib import Path\nREPO_ROOT = str(Path(__file__).resolve().parents[1])\n" + content
    
    # Replace absolute string paths
    content = content.replace(r'REPO_ROOT', "REPO_ROOT")
    content = content.replace(r'REPO_ROOT', "REPO_ROOT")
    content = content.replace(r"REPO_ROOT", "REPO_ROOT")
    content = content.replace(r"rREPO_ROOT", "REPO_ROOT")
    content = content.replace(REPO_ROOT, "REPO_ROOT") # fallbacks

    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "locations", "bucuresti_100km_places.csv")", r'os.path.join(REPO_ROOT, "reports", "locations", "bucuresti_100km_places.csv")')
    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")", r'os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")')
    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "seo", "indexing_manifest.json")", r'os.path.join(REPO_ROOT, "reports", "seo", "indexing_manifest.json")')
    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "seo", "qa_report.json")", r'os.path.join(REPO_ROOT, "reports", "seo", "qa_report.json")')
    content = content.replace(r"os.path.join(REPO_ROOT, "src", "pages", "petreceri")", r'os.path.join(REPO_ROOT, "src", "pages", "petreceri")')
    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "seo")", r'os.path.join(REPO_ROOT, "reports", "seo")')
    content = content.replace(r"os.path.join(REPO_ROOT, "src", "pages")", r'os.path.join(REPO_ROOT, "src", "pages")')

    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "seo", "indexing_manifest.json")", r'os.path.join(REPO_ROOT, "reports", "seo", "indexing_manifest.json")')
    content = content.replace(r"os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")", r'os.path.join(REPO_ROOT, "reports", "locations", "locations_100km.json")')

    if content != original:
        with open(s, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {s}")
