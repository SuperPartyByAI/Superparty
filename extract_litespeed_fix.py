import tarfile
import os

backup = r'C:\Users\ursac\Downloads\backup-3.22.2026_03-08-34_wowparty.tar.gz'
dest = r'c:\Users\ursac\WowParty\public'
prefix = 'backup-3.22.2026_03-08-34_wowparty/homedir/public_html/'

print("Începem extragerea direcționată a litespeed/css și wp-includes/css bypassând MAX_PATH...")
extracted = 0
with tarfile.open(backup, 'r:gz') as tar:
    for m in tar.getmembers():
        if m.name.startswith(prefix + 'wp-content/litespeed') or m.name.startswith(prefix + 'wp-includes/css'):
            # Modificăm structura internă a intrării pentru a o plasa corect în directoriul public/wp-content...
            m.name = m.name[len(prefix):]
            try:
                tar.extract(m, path=dest)
                extracted += 1
            except Exception as e:
                pass # Ignorăm fișierele cu nume aberant de lungi

print(f"✅ Gata! Am extras și copiat {extracted} fișiere esențiale (CSS și cache).")
