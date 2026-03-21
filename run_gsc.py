import os
import sys

found = False
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                creds = line[len('GOOGLE_APPLICATION_CREDENTIALS='):].strip()
                # Remove surrounding quotes if they exist
                if creds.startswith("'") and creds.endswith("'"):
                    creds = creds[1:-1]
                if creds.startswith('"') and creds.endswith('"'):
                    creds = creds[1:-1]
                with open('service_account.json', 'w', encoding='utf-8') as out:
                    out.write(creds)
                found = True
                print("Key extracted perfectly to service_account.json.")
                break
except Exception as e:
    print(f"Error reading .env: {e}")

if found:
    os.system('python scripts/gsc_submit.py --site https://www.superparty.ro/ --sitemap https://www.superparty.ro/sitemap-index.xml --key service_account.json')
else:
    print("Could not find credentials in .env")
