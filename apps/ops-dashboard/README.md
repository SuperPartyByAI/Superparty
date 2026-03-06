# Deploy Guide — Ops Dashboard (ops.superparty.ro)

## Cerințe
- Node 20+ pe server Hetzner
- Nginx (reverse proxy)
- Domain `ops.superparty.ro` cu TLS (Let's Encrypt)
- Google Cloud Console OAuth 2.0 app configurat

## 1. Google Cloud Console
1. Console → APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
2. Application type: **Web application**
3. Authorized JavaScript origins: `https://ops.superparty.ro`
4. Authorized redirect URIs: `https://ops.superparty.ro/auth/google/callback`
5. Notezi **Client ID** și **Client Secret**

## 2. Setup pe server

```bash
# Pe Hetzner VPS
cd /srv
git clone https://github.com/SuperPartyByAI/Superparty.git superparty
cd superparty/apps/ops-dashboard

# Copy .env
cp .env.example .env
nano .env  # Completezi cu valorile reale

# Generare session secret random
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"

# Install + build
npm install
npm run build

# Data dir
mkdir -p /srv/ops-dashboard/data
```

## 3. systemd service

```bash
sudo nano /etc/systemd/system/superparty-ops.service
```

```ini
[Unit]
Description=Superparty SEO Ops Dashboard
After=network.target

[Service]
Type=simple
User=superparty
WorkingDirectory=/srv/superparty/apps/ops-dashboard
EnvironmentFile=/srv/superparty/apps/ops-dashboard/.env
ExecStart=/usr/bin/node dist/server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable superparty-ops
sudo systemctl start superparty-ops
sudo systemctl status superparty-ops
```

## 4. Nginx vhost

```bash
sudo nano /etc/nginx/sites-available/ops.superparty.ro
```

```nginx
server {
    listen 80;
    server_name ops.superparty.ro;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ops.superparty.ro;

    ssl_certificate     /etc/letsencrypt/live/ops.superparty.ro/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ops.superparty.ro/privkey.pem;

    # No-index (zona privata)
    add_header X-Robots-Tag "noindex, nofollow, noarchive" always;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer" always;

    access_log /var/log/nginx/ops-dashboard.access.log;
    error_log  /var/log/nginx/ops-dashboard.error.log;

    location / {
        proxy_pass http://127.0.0.1:8787;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ops.superparty.ro /etc/nginx/sites-enabled/
sudo certbot --nginx -d ops.superparty.ro
sudo nginx -t && sudo systemctl reload nginx
```

## 5. Verificare

```bash
# Health check (public)
curl https://ops.superparty.ro/healthz
# → {"status":"ok"}

# Dashboard (trebuie să ceara login)
curl -I https://ops.superparty.ro/seo
# → 302 redirect la /auth/login

# Logs
journalctl -u superparty-ops -f
```

## Kill switches (instantanee, fără deploy)

```bash
# Oprești tot agentul SEO
sudo -u superparty sh -c 'echo "SEO_FREEZE=1" >> /srv/superparty/.env'
sudo systemctl restart superparty-orchestrator

# Oprești doar experiments
sudo -u superparty sh -c 'echo "SEO_FREEZE_EXPERIMENTS=1" >> /srv/superparty/.env'

# Protejezi pilonul
sudo -u superparty sh -c 'echo "SEO_PILLAR_LOCK=1" >> /srv/superparty/.env'
```
