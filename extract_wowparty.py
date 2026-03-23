import tarfile
import os
import sys

backup_path = 'C:/Users/ursac/Downloads/backup-3.22.2026_03-08-34_wowparty.tar.gz'
dest_path = 'C:/Users/ursac/Downloads/hosterion-backup/wowparty-theme'

print(f"Pregătire extragere din {backup_path}...")
try:
    os.makedirs(dest_path, exist_ok=True)
    
    with tarfile.open(backup_path, 'r:gz') as tar:
        print("Caut directoarele de teme și upload-uri pentru WowParty (durează un pic scanarea)...")
        members = []
        for m in tar.getmembers():
            if 'wowparty/homedir/public_html/wp-content/themes' in m.name or 'wowparty/homedir/public_html/wp-content/uploads/202' in m.name:
                members.append(m)
        
        print(f"Am găsit {len(members)} fișiere pentru teme și imagini recente. Extragere...")
        tar.extractall(path=dest_path, members=members)
        
    print("Extragere completă cu succes!")
except Exception as e:
    print(f"Eroare: {str(e)}")
    sys.exit(1)
