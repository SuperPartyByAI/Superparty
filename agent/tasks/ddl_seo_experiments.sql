PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS seo_experiments (
  exp_id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL,

  -- identity
  url_path TEXT NOT NULL,           -- ex: /petreceri/otopeni
  page_url TEXT,                    -- ex: https://www.superparty.ro/petreceri/otopeni (din GSC)
  file_path TEXT NOT NULL,          -- ex: src/pages/petreceri/otopeni.astro

  exp_type TEXT NOT NULL,           -- ctr_title_desc
  status TEXT NOT NULL,             -- PLANNED | RUNNING_A | RUNNING_B | EVALUATING | WINNER | LOSER | REVERTED | ABORTED

  started_at TEXT NOT NULL,         -- YYYY-MM-DD
  ends_at TEXT NOT NULL,            -- YYYY-MM-DD (started_at + 21 zile)

  -- windows (cu latență GSC)
  baseline_start TEXT NOT NULL,     -- YYYY-MM-DD
  baseline_end TEXT NOT NULL,       -- YYYY-MM-DD
  variant_start TEXT NOT NULL,      -- YYYY-MM-DD
  variant_end TEXT,                -- YYYY-MM-DD (când evaluăm)

  -- snapshots
  baseline_clicks INTEGER DEFAULT 0,
  baseline_impressions INTEGER DEFAULT 0,
  baseline_avg_position REAL DEFAULT 99.0,

  variant_clicks INTEGER DEFAULT 0,
  variant_impressions INTEGER DEFAULT 0,
  variant_avg_position REAL DEFAULT 99.0,

  -- content for rollback
  baseline_title TEXT,
  baseline_description TEXT,

  variant_a_title TEXT,
  variant_a_description TEXT,

  variant_b_title TEXT,
  variant_b_description TEXT,

  -- decisions
  winner_variant TEXT,              -- A | B | NULL
  decision_reason TEXT,             -- text/json summary

  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_seo_experiments_site_status
ON seo_experiments(site_id, status);

CREATE UNIQUE INDEX IF NOT EXISTS uniq_running_per_page
ON seo_experiments(site_id, url_path, status)
WHERE status IN ('PLANNED','RUNNING_A','RUNNING_B','EVALUATING');

CREATE TABLE IF NOT EXISTS page_state (
  site_id TEXT NOT NULL,
  url_path TEXT NOT NULL,
  last_touched_at TEXT,             -- YYYY-MM-DD
  cooldown_until TEXT,              -- YYYY-MM-DD
  active_exp_id TEXT,               -- exp_id or NULL
  PRIMARY KEY (site_id, url_path)
);

CREATE INDEX IF NOT EXISTS idx_page_state_active
ON page_state(site_id, active_exp_id);
