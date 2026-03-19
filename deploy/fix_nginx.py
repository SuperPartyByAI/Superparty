"""Write minimal Nginx config to test — no add_header directives."""

conf = 'server {\n'
conf += '    listen 443 ssl;\n'
conf += '    server_name ops.superparty.ro;\n'
conf += '\n'
conf += '    ssl_certificate /etc/letsencrypt/live/ops.superparty.ro/fullchain.pem;\n'
conf += '    ssl_certificate_key /etc/letsencrypt/live/ops.superparty.ro/privkey.pem;\n'
conf += '\n'
conf += '    location /dashboard/ {\n'
conf += '        proxy_pass http://127.0.0.1:8092/;\n'
conf += '        proxy_set_header Host $host;\n'
conf += '        proxy_set_header X-Real-IP $remote_addr;\n'
conf += '    }\n'
conf += '\n'
conf += '    location /seo-new/ {\n'
conf += '        proxy_pass http://127.0.0.1:8091/;\n'
conf += '        proxy_set_header Host $host;\n'
conf += '        proxy_set_header X-Real-IP $remote_addr;\n'
conf += '    }\n'
conf += '\n'
conf += '    location / {\n'
conf += '        proxy_pass http://127.0.0.1:3000;\n'
conf += '        proxy_set_header Host $host;\n'
conf += '        proxy_set_header X-Real-IP $remote_addr;\n'
conf += '    }\n'
conf += '}\n'

import subprocess

target = "/etc/nginx/sites-enabled/ops.superparty.ro"
with open(target, "w") as f:
    f.write(conf)
print(f"Written {len(conf)} bytes")

result = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
if result.returncode == 0:
    subprocess.run(["systemctl", "reload", "nginx"])
    print("NGINX RELOADED OK")
else:
    print(f"NGINX TEST FAILED (exit {result.returncode})")
