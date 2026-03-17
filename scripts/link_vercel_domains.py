import requests
import os
import json

token = os.environ.get('VERCEL_TOKEN', 'your_token_here')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

domains = [
  '123party.ro', 'animatopia.ro', 'clubuldisney.ro', 'divertix.ro', 
  'joyparty.ro', 'kassia.ro', 'partymania.ro', 'petreceritematice.ro', 
  'planetparty.ro', 'playparty.ro', 'superparty.ro', 'teraparty.ro', 
  'universeparty.ro', 'ursitoaremagice.ro', 'youparty.ro'
]

print('Fetching projects...')
r = requests.get('https://api.vercel.com/v9/projects', headers=headers)
projs = r.json().get('projects', [])

for domain in domains:
    target_name = domain.replace('.ro', '-ro').replace('.', '-')
    proj = next((p for p in projs if p['name'] == target_name or p['name'] == domain), None)
    
    if proj:
        proj_id = proj['id']
        print(f'Adding domain {domain} to project {proj["name"]} ({proj_id})...')
        
        # Check if already added
        d_req = requests.get(f'https://api.vercel.com/v9/projects/{proj_id}/domains', headers=headers)
        exist_domains = [d['name'] for d in d_req.json().get('domains', [])]
        
        if domain in exist_domains:
            print(f'  ✓ Already added')
            continue

        add_url = f'https://api.vercel.com/v10/projects/{proj_id}/domains'
        res = requests.post(add_url, headers=headers, json={'name': domain})
        
        if res.status_code in [200, 201]:
            print(f'  ✓ Success')
        else:
            print(f'  X Failed: {res.text}')
    else:
        print(f'Project for {domain} not found!')
