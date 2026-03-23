import tarfile
import os
import sys

backup_path = r'C:\Users\ursac\Downloads\backup-3.22.2026_03-08-34_wowparty.tar.gz'
dest_path = r'C:\Users\ursac\Downloads\hosterion-backup\wowparty-theme'

print("Extragere foldere suplimentare litespeed si plugins...")
try:
    os.makedirs(dest_path, exist_ok=True)
    with tarfile.open(backup_path, 'r:gz') as tar:
        members = []
        for m in tar.getmembers():
            if 'wowparty/homedir/public_html/wp-content/litespeed' in m.name or 'wowparty/homedir/public_html/wp-content/plugins' in m.name or 'wowparty/homedir/public_html/wp-includes/css' in m.name:
                members.append(m)
        
        print(f"Am găsit {len(members)} fișiere suplimentare (litespeed, plugins, wp-includes/css). Extragere...")
        tar.extractall(path=dest_path, members=members)
    print("Extragere completă!")
except Exception as e:
    print("Eroare:", e)
    sys.exit(1)
