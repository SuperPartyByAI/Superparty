# Ops Dashboard Cutover — Runbook de Infrastructură Server

## Context
Există două dashboarduri în sistem:

| Dashboard | Generator | Output | Status |
|---|---|---|---|
| **NOU (Principal)** | `scripts/seo_ops_dashboard.py` | `reports/superparty/ops_dashboard.html` | ✅ Sursa de adevăr L6/L7 |
| **Legacy (Deprecat)** | `scripts/seo_dashboard.py` | `reports/seo/dashboard.html` | ❌ Cuplat la artefacte L3/L4, neconectat la L6/L7 |

> **Regula operatorului:** Nu deschide `reports/seo/dashboard.html` ca sursă de adevăr operațională. El nu urmărește L6/L7.

---

## Pasul 1 — Generarea dashboardului nou

```bash
cd /srv/superparty
python3 scripts/seo_ops_dashboard.py
```

Output: `/srv/superparty/reports/superparty/ops_dashboard.html`

---

## Pasul 2 — Servire locală pentru verificare imediată (debug/test)

```bash
cd /srv/superparty
python3 -m http.server 8091 --bind 127.0.0.1 --directory reports/superparty
```

Verificare:
```bash
curl http://127.0.0.1:8091/ops_dashboard.html | head -30
```

---

## Pasul 3 — Instalare ca serviciu permanent (SystemD)

Fișierul de serviciu este versioned în repo la:
`infra/systemd/seo-ops-dashboard.service`

Instalare pe server:
```bash
cp /srv/superparty/infra/systemd/seo-ops-dashboard.service /etc/systemd/system/
chmod 644 /etc/systemd/system/seo-ops-dashboard.service
systemctl daemon-reload
systemctl enable seo-ops-dashboard
systemctl start seo-ops-dashboard
systemctl status seo-ops-dashboard
```

---

## Pasul 4 — Configurare Nginx pentru ops.superparty.ro/seo-new

Adaugă în blocul `server` pentru `ops.superparty.ro`:

```nginx
# Redirect de la /seo-new la fișierul dashboard principal
location = /seo-new {
    return 302 /seo-new/ops_dashboard.html;
}

location /seo-new/ {
    proxy_pass         http://127.0.0.1:8091/;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
```

Test și reload:
```bash
nginx -t && systemctl reload nginx
```

URL primar după cutover:
```
https://ops.superparty.ro/seo-new/ops_dashboard.html
```

---

## Pasul 5 — Dashboard legacy (rută separată)

Dacă vrei să păstrezi accesul la dashboardul vechi pentru referință istorică, adaugă o rută separată:

```nginx
location /seo-legacy/ {
    proxy_pass http://127.0.0.1:8090/;    # portul care servea dashboard-ul vechi, dacă există
}
```

Sau pur și simplu lasă `reports/seo/dashboard.html` neatins — nu este servit activ și nu are impact.

---

## Pasul 6 — Refresh periodic automat (cron)

Adaugă în crontab-ul serverului pentru refresh la fiecare 15 minute:
```bash
# Regenerare dashboard L6/L7
*/15 * * * * cd /srv/superparty && /usr/bin/python3 scripts/seo_ops_dashboard.py >> /tmp/seo_ops_dashboard_refresh.log 2>&1
```

---

## Rezumat URL-uri

| URL | Descriere | Status |
|---|---|---|
| `https://ops.superparty.ro/seo-new/ops_dashboard.html` | Dashboard Principal L6/L7 | ✅ Sursa de adevăr |
| `reports/seo/dashboard.html` (fișier local) | Dashboard Legacy L3/L4 | ❌ Nu folosiți operațional |

---

## Note importante

- **PR-ul acesta pregătește cutover-ul și include fișierul SystemD versioned.**
- **Cutover-ul live (Nginx + SystemD pe server) se execută manual de operator** urmând pașii din acest runbook.
- **PR-ul nu modifică configurații live** — ele nu sunt versionate în repo.
