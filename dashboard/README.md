# SEO Agent Dashboard

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn

# Set env vars
set SUPABASE_URL=https://cijvmpxctjnqniyfhlny.supabase.co
set SUPABASE_KEY=your-service-role-key

# Start API (port 8000)
cd dashboard
uvicorn api:app --reload --port 8000

# Open frontend
# Open dashboard/index.html in browser (or serve via any static server)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/sites` | List sites + freeze status |
| GET | `/api/prs` | PR queue (filter: `?status=pending`) |
| GET | `/api/metrics` | Monitor metrics |
| GET | `/api/alerts` | Audit log entries |
| GET | `/api/head-terms` | Head terms + owners |
| GET | `/api/owner-pages` | Owner pages |
| GET | `/api/embeddings/stats` | Embedding statistics |
| POST | `/api/action/approve-pr` | Approve PR `{ pr_id, actor }` |
| POST | `/api/action/reject-pr` | Reject PR |
| POST | `/api/action/revert-pr` | Mark for rollback |
| POST | `/api/action/freeze` | Set/clear freeze `{ domain, freeze_until }` |

## Architecture

```
dashboard/
├── api.py          # FastAPI backend (connects to Supabase)
├── index.html      # Single-file frontend (no build step)
└── README.md
```

- **Backend**: FastAPI with stdlib `urllib` (no `supabase-py` dependency)
- **Frontend**: Vanilla JS + CSS (dark glassmorphism design)
- **Auth**: None (local dev). Add middleware for production.
- **All actions write to `audit_logs`** for traceability.
